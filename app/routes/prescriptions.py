from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from app.crud import prescription as prescription_crud
from app.crud import patient as patient_crud
from app.crud import doctor as doctor_crud

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def prescription_list(request: Request, db: Session = Depends(get_db)):
    prescriptions = prescription_crud.get_prescriptions_with_details(db)
    return templates.TemplateResponse("prescriptions/index.html", {
        "request": request,
        "prescriptions": prescriptions,
        "title": "Prescription List"
    })

@router.get("/patient/{patient_id}", response_class=HTMLResponse)
async def patient_prescriptions(request: Request, patient_id: int, db: Session = Depends(get_db)):
    """List prescriptions for a specific patient"""
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    prescriptions = prescription_crud.get_prescriptions_by_patient(db, patient_id)
    return templates.TemplateResponse("prescriptions/patient_prescriptions.html", {
        "request": request,
        "patient": patient,
        "prescriptions": prescriptions,
        "title": f"Prescriptions - {patient.name}"
    })

@router.get("/add", response_class=HTMLResponse)
async def add_prescription_form(request: Request, patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Show add prescription form"""
    patients = patient_crud.get_patients_with_doctor(db)
    doctors = doctor_crud.get_doctors(db)
    
    selected_patient = None
    if patient_id:
        selected_patient = patient_crud.get_patient(db, patient_id)
    
    return templates.TemplateResponse("prescriptions/add.html", {
        "request": request,
        "patients": patients,
        "doctors": doctors,
        "selected_patient": selected_patient,
        "today": date.today().isoformat(),
        "title": "Add Prescription"
    })

@router.post("/add", response_class=HTMLResponse)
async def create_prescription(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    diagnosis: str = Form(...),
    medicines: Optional[str] = Form(None),
    dosage_instructions: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    prescription_date: date = Form(...),
    valid_until: Optional[date] = Form(None),
    follow_up_date: Optional[date] = Form(None),
    follow_up_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new prescription"""
    # Validate patient and doctor exist
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        patients = patient_crud.get_patients_with_doctor(db)
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("prescriptions/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "error": "Patient not found",
            "title": "Add Prescription"
        })
    
    doctor = doctor_crud.get_doctor(db, doctor_id)
    if not doctor:
        patients = patient_crud.get_patients_with_doctor(db)
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("prescriptions/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "error": "Doctor not found",
            "title": "Add Prescription"
        })
    
    # Create prescription data
    prescription_data = PrescriptionCreate(
        patient_id=patient_id,
        doctor_id=doctor_id,
        diagnosis=diagnosis,
        medicines=medicines,
        dosage_instructions=dosage_instructions,
        notes=notes,
        prescription_date=prescription_date,
        valid_until=valid_until,
        is_active=True,
        follow_up_date=follow_up_date,
        follow_up_notes=follow_up_notes
    )
    
    # Create prescription
    prescription = prescription_crud.create_prescription(db, prescription_data)
    
    return RedirectResponse(url=f"/prescriptions/view/{prescription.id}", status_code=303)

@router.get("/edit/{prescription_id}", response_class=HTMLResponse)
async def edit_prescription_form(request: Request, prescription_id: int, db: Session = Depends(get_db)):
    """Show edit prescription form"""
    prescription = prescription_crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    patients = patient_crud.get_patients_with_doctor(db)
    doctors = doctor_crud.get_doctors(db)
    
    return templates.TemplateResponse("prescriptions/edit.html", {
        "request": request,
        "prescription": prescription,
        "patients": patients,
        "doctors": doctors,
        "title": f"Edit Prescription - {prescription.prescription_code}"
    })

@router.post("/edit/{prescription_id}")
async def update_prescription(
    request: Request,
    prescription_id: int,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    diagnosis: str = Form(...),
    medicines: Optional[str] = Form(None),
    dosage_instructions: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    prescription_date: date = Form(...),
    valid_until: Optional[date] = Form(None),
    follow_up_date: Optional[date] = Form(None),
    follow_up_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update prescription"""
    prescription_data = PrescriptionUpdate(
        patient_id=patient_id,
        doctor_id=doctor_id,
        diagnosis=diagnosis,
        medicines=medicines,
        dosage_instructions=dosage_instructions,
        notes=notes,
        prescription_date=prescription_date,
        valid_until=valid_until,
        follow_up_date=follow_up_date,
        follow_up_notes=follow_up_notes
    )
    
    updated = prescription_crud.update_prescription(db, prescription_id, prescription_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    return RedirectResponse(url=f"/prescriptions/view/{prescription_id}", status_code=303)

@router.get("/view/{prescription_id}", response_class=HTMLResponse)
async def view_prescription(request: Request, prescription_id: int, db: Session = Depends(get_db)):
    """View prescription details"""
    prescription = prescription_crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    return templates.TemplateResponse("prescriptions/view.html", {
        "request": request,
        "prescription": prescription,
        "title": f"Prescription - {prescription.prescription_code}"
    })

@router.get("/print/{prescription_id}", response_class=HTMLResponse)
async def print_prescription(request: Request, prescription_id: int, db: Session = Depends(get_db)):
    """Print prescription (clean layout for printing)"""
    prescription = prescription_crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    return templates.TemplateResponse("prescriptions/print.html", {
        "request": request,
        "prescription": prescription,
        "title": f"Print Prescription - {prescription.prescription_code}"
    })

@router.post("/toggle-status/{prescription_id}")
async def toggle_prescription_status(
    prescription_id: int,
    db: Session = Depends(get_db)
):
    """Toggle prescription status"""
    prescription = prescription_crud.toggle_prescription_status(db, prescription_id)

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    return RedirectResponse(
        url="/prescriptions",
        status_code=303
    )

@router.post("/delete/{prescription_id}")
async def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Delete prescription"""
    success = prescription_crud.delete_prescription(db, prescription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return RedirectResponse(url="/prescriptions", status_code=303)

# API Routes
@router.get("/api", response_model=list)
async def api_get_prescriptions(
    skip: int = 0, 
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """API endpoint for prescriptions"""
    return prescription_crud.get_prescriptions(db, skip, limit, patient_id, doctor_id, is_active)

@router.get("/api/{prescription_id}")
async def api_get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Get single prescription via API"""
    prescription = prescription_crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.post("/api")
async def api_create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    """Create prescription via API"""
    return prescription_crud.create_prescription(db, prescription)

@router.put("/api/{prescription_id}")
async def api_update_prescription(prescription_id: int, prescription: PrescriptionUpdate, db: Session = Depends(get_db)):
    """Update prescription via API"""
    updated = prescription_crud.update_prescription(db, prescription_id, prescription)
    if not updated:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return updated

@router.delete("/api/{prescription_id}")
async def api_delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    """Delete prescription via API"""
    success = prescription_crud.delete_prescription(db, prescription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deleted successfully"}

@router.get("/api/patient/{patient_id}")
async def api_get_patient_prescriptions(patient_id: int, db: Session = Depends(get_db)):
    """Get all prescriptions for a patient via API"""
    return prescription_crud.get_prescriptions_by_patient(db, patient_id)