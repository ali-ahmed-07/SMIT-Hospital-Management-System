from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.billing import BillCreate, BillUpdate, BillItemCreate
from app.crud import billing as billing_crud
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment

router = APIRouter(prefix="/billing", tags=["Billing"])
templates = Jinja2Templates(directory="app/templates")


async def _parse_items_from_form(request: Request):
    """
    Reads dynamic item rows submitted as description[], quantity[], unit_price[]
    (see the JS in add.html / edit.html which builds these array fields).
    """
    form = await request.form()
    descriptions = form.getlist("description[]")
    quantities = form.getlist("quantity[]")
    prices = form.getlist("unit_price[]")

    items = []
    for desc, qty, price in zip(descriptions, quantities, prices):
        if not desc or not str(desc).strip():
            continue
        items.append(BillItemCreate(
            description=str(desc).strip(),
            quantity=float(qty) if qty else 1.0,
            unit_price=float(price) if price else 0.0
        ))
    return items


# ==================== HTML ROUTES ====================

@router.get("/", response_class=HTMLResponse)
async def bill_list(request: Request, db: Session = Depends(get_db)):
    """List all bills"""
    try:
        bills = billing_crud.get_bills(db)
        return templates.TemplateResponse("billing/index.html", {
            "request": request,
            "bills": bills,
            "title": "Billing"
        })
    except Exception as e:
        print(f"Error in bill_list: {e}")
        return templates.TemplateResponse("billing/index.html", {
            "request": request,
            "bills": [],
            "title": "Billing",
            "error": str(e)
        })


@router.get("/add", response_class=HTMLResponse)
async def add_bill_form(
    request: Request,
    patient_id: Optional[int] = None,
    appointment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Show create bill form"""
    try:
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        appointments = db.query(Appointment).all()
        return templates.TemplateResponse("billing/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "appointments": appointments,
            "selected_patient_id": patient_id,
            "selected_appointment_id": appointment_id,
            "today": date.today().isoformat(),
            "title": "Create Bill"
        })
    except Exception as e:
        print(f"Error in add_bill_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add", response_class=HTMLResponse)
async def create_bill(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    appointment_id: Optional[str] = Form(None),
    bill_date: date = Form(...),
    discount_percent: float = Form(0),
    tax_percent: float = Form(0),
    paid_amount: float = Form(0),
    payment_method: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new bill with line items"""
    patients = db.query(Patient).all()
    doctors = db.query(Doctor).all()
    appointments = db.query(Appointment).all()

    try:
        items = await _parse_items_from_form(request)
        if not items:
            raise ValueError("Please add at least one billing item")

        bill_data = BillCreate(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=int(appointment_id) if appointment_id else None,
            bill_date=bill_date,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            paid_amount=paid_amount,
            payment_method=payment_method,
            notes=notes,
            items=items
        )
        billing_crud.create_bill(db, bill_data)
        return RedirectResponse(url="/billing", status_code=303)

    except Exception as e:
        print(f"Error in create_bill: {e}")
        return templates.TemplateResponse("billing/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "appointments": appointments,
            "error": str(e),
            "today": date.today().isoformat(),
            "title": "Create Bill"
        })


@router.get("/view/{bill_id}", response_class=HTMLResponse)
async def view_bill(request: Request, bill_id: int, db: Session = Depends(get_db)):
    """View bill / invoice details"""
    try:
        bill = billing_crud.get_bill(db, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        return templates.TemplateResponse("billing/view.html", {
            "request": request,
            "bill": bill,
            "title": f"Bill - {bill.bill_code}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in view_bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edit/{bill_id}", response_class=HTMLResponse)
async def edit_bill_form(request: Request, bill_id: int, db: Session = Depends(get_db)):
    """Show edit bill form"""
    try:
        bill = billing_crud.get_bill(db, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        appointments = db.query(Appointment).all()

        return templates.TemplateResponse("billing/edit.html", {
            "request": request,
            "bill": bill,
            "patients": patients,
            "doctors": doctors,
            "appointments": appointments,
            "title": f"Edit Bill - {bill.bill_code}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in edit_bill_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit/{bill_id}")
async def update_bill(
    request: Request,
    bill_id: int,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    appointment_id: Optional[str] = Form(None),
    bill_date: date = Form(...),
    discount_percent: float = Form(0),
    tax_percent: float = Form(0),
    paid_amount: float = Form(0),
    payment_method: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update a bill (recalculates totals)"""
    try:
        items = await _parse_items_from_form(request)

        bill_data = BillUpdate(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=int(appointment_id) if appointment_id else None,
            bill_date=bill_date,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            paid_amount=paid_amount,
            payment_method=payment_method,
            notes=notes,
            items=items if items else None
        )
        updated = billing_crud.update_bill(db, bill_id, bill_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Bill not found")

        return RedirectResponse(url="/billing", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pay/{bill_id}")
async def pay_bill(bill_id: int, amount: float = Form(...), db: Session = Depends(get_db)):
    """Record a payment against a bill"""
    try:
        bill = billing_crud.record_payment(db, bill_id, amount)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        return RedirectResponse(url=f"/billing/view/{bill_id}", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in pay_bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete/{bill_id}")
async def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """Delete a bill"""
    try:
        success = billing_crud.delete_bill(db, bill_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bill not found")
        return RedirectResponse(url="/billing", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== API ROUTES ====================

@router.get("/api")
async def api_get_bills(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return billing_crud.get_bills(db, skip, limit, patient_id, doctor_id, payment_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/{bill_id}")
async def api_get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = billing_crud.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.post("/api")
async def api_create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    try:
        return billing_crud.create_bill(db, bill)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/{bill_id}")
async def api_update_bill(bill_id: int, bill: BillUpdate, db: Session = Depends(get_db)):
    updated = billing_crud.update_bill(db, bill_id, bill)
    if not updated:
        raise HTTPException(status_code=404, detail="Bill not found")
    return updated


@router.delete("/api/{bill_id}")
async def api_delete_bill(bill_id: int, db: Session = Depends(get_db)):
    success = billing_crud.delete_bill(db, bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}


@router.get("/api/patient/{patient_id}")
async def api_get_patient_bills(patient_id: int, db: Session = Depends(get_db)):
    return billing_crud.get_bills_by_patient(db, patient_id)
