from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.crud import doctor as doctor_crud

router = APIRouter(prefix="/doctors", tags=["Doctors"])
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def doctor_list(request: Request, db: Session = Depends(get_db)):
    doctors = doctor_crud.get_doctors(db)
    return templates.TemplateResponse("doctors/index.html", {
        "request": request,
        "doctors": doctors,
        "title": "Doctor List"
    })

@router.get("/add", response_class=HTMLResponse)
async def add_doctor_form(request: Request, db: Session = Depends(get_db)):
    next_code = doctor_crud.generate_doctor_code(db)
    return templates.TemplateResponse("doctors/add.html", {
        "request": request,
        "next_code": next_code,
        "title": "Add Doctor"
    })

@router.post("/add")
async def create_doctor(
    request: Request,
    name: str = Form(...),
    specialization: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    salary: Decimal = Form(...),
    gender: str = Form(...),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    doctor_code = doctor_crud.generate_doctor_code(db)  # 👈 auto-generated

    doctor_data = DoctorCreate(
        doctor_code=doctor_code,
        name=name,
        specialization=specialization,
        email=email,
        phone=phone,
        salary=salary,
        gender=gender,
        address=address
    )

    doctor_crud.create_doctor(db, doctor_data)
    return RedirectResponse(url="/doctors", status_code=303)
    
    # Check if doctor_code already exists
    existing = doctor_crud.get_doctor_by_code(db, doctor_code)
    if existing:
        return templates.TemplateResponse("doctors/add.html", {
            "request": request,
            "error": "Doctor code already exists",
            "title": "Add Doctor"
        })
    
    doctor_data = DoctorCreate(
        doctor_code=doctor_code,
        name=name,
        specialization=specialization,
        email=email,
        phone=phone,
        salary=salary,
        gender=gender,
        address=address
    )
    
    doctor_crud.create_doctor(db, doctor_data)
    return RedirectResponse(url="/doctors", status_code=303)

@router.get("/edit/{doctor_id}", response_class=HTMLResponse)
async def edit_doctor_form(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return templates.TemplateResponse("doctors/edit.html", {
        "request": request,
        "doctor": doctor,
        "title": "Edit Doctor"
    })

@router.post("/edit/{doctor_id}")
async def update_doctor(
    request: Request,
    doctor_id: int,
    name: str = Form(...),
    specialization: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    salary: Decimal = Form(...),
    gender: str = Form(...),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    doctor_data = DoctorUpdate(
        name=name,
        specialization=specialization,
        email=email,
        phone=phone,
        salary=salary,
        gender=gender,
        address=address
    )
    
    updated = doctor_crud.update_doctor(db, doctor_id, doctor_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return RedirectResponse(url="/doctors", status_code=303)

@router.get("/view/{doctor_id}", response_class=HTMLResponse)
async def view_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return templates.TemplateResponse("doctors/view.html", {
        "request": request,
        "doctor": doctor,
        "title": "View Doctor"
    })

@router.post("/delete/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    success = doctor_crud.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return RedirectResponse(url="/doctors", status_code=303)

@router.post("/toggle-status/{doctor_id}")
async def toggle_doctor_status(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_crud.toggle_status(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return RedirectResponse(url="/doctors", status_code=303)

# API Routes
@router.get("/api", response_model=list)
async def api_get_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return doctor_crud.get_doctors(db, skip, limit)

@router.get("/api/{doctor_id}")
async def api_get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_crud.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.post("/api")
async def api_create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    existing = doctor_crud.get_doctor_by_code(db, doctor.doctor_code)
    if existing:
        raise HTTPException(status_code=400, detail="Doctor code already exists")
    return doctor_crud.create_doctor(db, doctor)

@router.put("/api/{doctor_id}")
async def api_update_doctor(doctor_id: int, doctor: DoctorUpdate, db: Session = Depends(get_db)):
    updated = doctor_crud.update_doctor(db, doctor_id, doctor)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated

@router.delete("/api/{doctor_id}")
async def api_delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    success = doctor_crud.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted successfully"}