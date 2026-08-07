from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.schemas.staff import StaffCreate, StaffUpdate
from app.crud import staff as staff_crud
from app.crud import doctor as doctor_crud

router = APIRouter(prefix="/staff", tags=["Staff"])
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def staff_list(request: Request, db: Session = Depends(get_db)):
    staff_members = staff_crud.get_staff_with_doctor(db)
    return templates.TemplateResponse("staff/index.html", {
        "request": request,
        "staff_members": staff_members,
        "title": "Staff Management"
    })

@router.get("/add", response_class=HTMLResponse)
async def add_staff_form(request: Request, db: Session = Depends(get_db)):
    doctors = doctor_crud.get_doctors(db)
    next_code = staff_crud.generate_staff_code(db)
    return templates.TemplateResponse("staff/add.html", {
        "request": request,
        "doctors": doctors,
        "next_code": next_code,
        "title": "Add Staff Member"
    })

@router.post("/add")
async def create_staff(
    request: Request,
    doctor_id: Optional[int] = Form(None),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    department: str = Form(...),
    designation: str = Form(...),
    salary: Decimal = Form(...),
    joining_date: date = Form(...),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing = staff_crud.get_staff_by_email(db, email)
    if existing:
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("staff/add.html", {
            "request": request,
            "doctors": doctors,
            "next_code": staff_crud.generate_staff_code(db),
            "error": "Email already exists",
            "title": "Add Staff Member"
        })
    
    # Validate salary
    if salary < 0:
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("staff/add.html", {
            "request": request,
            "doctors": doctors,
            "next_code": staff_crud.generate_staff_code(db),
            "error": "Salary must be greater than 0",
            "title": "Add Staff Member"
        })
    
    staff_code = staff_crud.generate_staff_code(db)
    
    staff_data = StaffCreate(
        staff_code=staff_code,
        doctor_id=doctor_id,
        name=name,
        email=email,
        phone=phone,
        department=department,
        designation=designation,
        salary=salary,
        joining_date=joining_date,
        address=address
    )
    
    staff_crud.create_staff(db, staff_data)
    return RedirectResponse(url="/staff", status_code=303)

@router.get("/edit/{staff_id}", response_class=HTMLResponse)
async def edit_staff_form(request: Request, staff_id: int, db: Session = Depends(get_db)):
    staff_member = staff_crud.get_staff(db, staff_id)
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    doctors = doctor_crud.get_doctors(db)
    return templates.TemplateResponse("staff/edit.html", {
        "request": request,
        "staff": staff_member,
        "doctors": doctors,
        "title": "Edit Staff Member"
    })

@router.post("/edit/{staff_id}")
async def update_staff(
    request: Request,
    staff_id: int,
    doctor_id: Optional[int] = Form(None),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    department: str = Form(...),
    designation: str = Form(...),
    salary: Decimal = Form(...),
    joining_date: date = Form(...),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Check if email already exists for another staff member
    existing = staff_crud.get_staff_by_email(db, email)
    if existing and existing.id != staff_id:
        staff_member = staff_crud.get_staff(db, staff_id)
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("staff/edit.html", {
            "request": request,
            "staff": staff_member,
            "doctors": doctors,
            "error": "Email already exists for another staff member",
            "title": "Edit Staff Member"
        })
    
    # Validate salary
    if salary < 0:
        staff_member = staff_crud.get_staff(db, staff_id)
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("staff/edit.html", {
            "request": request,
            "staff": staff_member,
            "doctors": doctors,
            "error": "Salary must be greater than 0",
            "title": "Edit Staff Member"
        })
    
    staff_data = StaffUpdate(
        doctor_id=doctor_id,
        name=name,
        email=email,
        phone=phone,
        department=department,
        designation=designation,
        salary=salary,
        joining_date=joining_date,
        address=address
    )
    
    updated = staff_crud.update_staff(db, staff_id, staff_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return RedirectResponse(url="/staff", status_code=303)

@router.get("/view/{staff_id}", response_class=HTMLResponse)
async def view_staff(request: Request, staff_id: int, db: Session = Depends(get_db)):
    staff_member = staff_crud.get_staff(db, staff_id)
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return templates.TemplateResponse("staff/view.html", {
        "request": request,
        "staff": staff_member,
        "title": "View Staff Member"
    })

@router.post("/delete/{staff_id}")
async def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    success = staff_crud.delete_staff(db, staff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return RedirectResponse(url="/staff", status_code=303)

@router.post("/toggle-status/{staff_id}")
async def toggle_staff_status(staff_id: int, db: Session = Depends(get_db)):
    staff_member = staff_crud.toggle_staff_status(db, staff_id)
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return RedirectResponse(url="/staff", status_code=303)

# API Routes
@router.get("/api")
async def api_get_staff(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return staff_crud.get_all_staff(db, skip, limit)

@router.get("/api/{staff_id}")
async def api_get_staff_by_id(staff_id: int, db: Session = Depends(get_db)):
    staff_member = staff_crud.get_staff(db, staff_id)
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff_member

@router.post("/api")
async def api_create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    existing = staff_crud.get_staff_by_email(db, staff.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    return staff_crud.create_staff(db, staff)

@router.put("/api/{staff_id}")
async def api_update_staff(staff_id: int, staff: StaffUpdate, db: Session = Depends(get_db)):
    updated = staff_crud.update_staff(db, staff_id, staff)
    if not updated:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return updated

@router.delete("/api/{staff_id}")
async def api_delete_staff(staff_id: int, db: Session = Depends(get_db)):
    success = staff_crud.delete_staff(db, staff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return {"message": "Staff member deleted successfully"}