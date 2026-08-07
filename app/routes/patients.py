from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate
from app.crud import patient as patient_crud
from app.crud import doctor as doctor_crud

router = APIRouter(prefix="/patients", tags=["Patients"])
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def patient_list(request: Request, db: Session = Depends(get_db)):
    patients = patient_crud.get_patients_with_doctor(db)
    return templates.TemplateResponse("patients/index.html", {
        "request": request,
        "patients": patients,
        "title": "Patient List"
    })

@router.get("/add", response_class=HTMLResponse)
async def add_patient_form(request: Request, db: Session = Depends(get_db)):
    doctors = doctor_crud.get_doctors(db)
    next_code = patient_crud.generate_patient_code(db)
    return templates.TemplateResponse("patients/add.html", {
        "request": request,
        "doctors": doctors,
        "next_code": next_code,
        "title": "Add Patient"
    })

@router.post("/add")
async def create_patient(
    request: Request,
    doctor_id: int = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    disease: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    admission_date: date = Form(...),
    discharge_date: Optional[date] = Form(None),
    db: Session = Depends(get_db)
):
    if age < 0 or age > 150:
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("patients/add.html", {
            "request": request,
            "doctors": doctors,
            "next_code": patient_crud.generate_patient_code(db),
            "error": "Age must be between 0 and 150",
            "title": "Add Patient"
        })

    patient_code = patient_crud.generate_patient_code(db)  # 👈 auto-generated

    patient_data = PatientCreate(
        patient_code=patient_code,
        doctor_id=doctor_id,
        name=name,
        age=age,
        gender=gender,
        disease=disease,
        phone=phone,
        address=address,
        admission_date=admission_date,
        discharge_date=discharge_date
    )

    patient_crud.create_patient(db, patient_data)
    return RedirectResponse(url="/patients", status_code=303)
    
    # Check if patient_code already exists
    existing = patient_crud.get_patient_by_code(db, patient_code)
    if existing:
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("patients/add.html", {
            "request": request,
            "doctors": doctors,
            "error": "Patient code already exists",
            "title": "Add Patient"
        })
    
    # Validate age
    if age < 0 or age > 150:
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("patients/add.html", {
            "request": request,
            "doctors": doctors,
            "error": "Age must be between 0 and 150",
            "title": "Add Patient"
        })
    
    patient_data = PatientCreate(
        patient_code=patient_code,
        doctor_id=doctor_id,
        name=name,
        age=age,
        gender=gender,
        disease=disease,
        phone=phone,
        address=address,
        admission_date=admission_date,
        discharge_date=discharge_date
    )
    
    patient_crud.create_patient(db, patient_data)
    return RedirectResponse(url="/patients", status_code=303)

@router.get("/edit/{patient_id}", response_class=HTMLResponse)
async def edit_patient_form(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    doctors = doctor_crud.get_doctors(db)
    return templates.TemplateResponse("patients/edit.html", {
        "request": request,
        "patient": patient,
        "doctors": doctors,
        "title": "Edit Patient"
    })

@router.post("/edit/{patient_id}")
async def update_patient(
    request: Request,
    patient_id: int,
    doctor_id: int = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    disease: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    admission_date: date = Form(...),
    discharge_date: Optional[date] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate age
    if age < 0 or age > 150:
        patient = patient_crud.get_patient(db, patient_id)
        doctors = doctor_crud.get_doctors(db)
        return templates.TemplateResponse("patients/edit.html", {
            "request": request,
            "patient": patient,
            "doctors": doctors,
            "error": "Age must be between 0 and 150",
            "title": "Edit Patient"
        })
    
    patient_data = PatientUpdate(
        doctor_id=doctor_id,
        name=name,
        age=age,
        gender=gender,
        disease=disease,
        phone=phone,
        address=address,
        admission_date=admission_date,
        discharge_date=discharge_date
    )
    
    updated = patient_crud.update_patient(db, patient_id, patient_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return RedirectResponse(url="/patients", status_code=303)

@router.get("/view/{patient_id}", response_class=HTMLResponse)
async def view_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("patients/view.html", {
        "request": request,
        "patient": patient,
        "title": "View Patient"
    })

@router.post("/delete/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    success = patient_crud.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return RedirectResponse(url="/patients", status_code=303)

@router.post("/toggle-status/{patient_id}")
async def toggle_patient_status(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.toggle_status(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return RedirectResponse(url="/patients", status_code=303)

# API Routes
@router.get("/api", response_model=list)
async def api_get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return patient_crud.get_patients(db, skip, limit)

@router.get("/api/{patient_id}")
async def api_get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/api")
async def api_create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    existing = patient_crud.get_patient_by_code(db, patient.patient_code)
    if existing:
        raise HTTPException(status_code=400, detail="Patient code already exists")
    return patient_crud.create_patient(db, patient)

@router.put("/api/{patient_id}")
async def api_update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    updated = patient_crud.update_patient(db, patient_id, patient)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated

@router.delete("/api/{patient_id}")
async def api_delete_patient(patient_id: int, db: Session = Depends(get_db)):
    success = patient_crud.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}