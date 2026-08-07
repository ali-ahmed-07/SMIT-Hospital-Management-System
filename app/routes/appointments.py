from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, time

from app.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.crud import appointment as appointment_crud
from app.crud import patient as patient_crud
from app.crud import doctor as doctor_crud
from app.crud import staff as staff_crud
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.staff import Staff

router = APIRouter(prefix="/appointments", tags=["Appointments"])
templates = Jinja2Templates(directory="app/templates")

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def appointment_list(request: Request, db: Session = Depends(get_db)):
    """List all appointments"""
    try:
        appointments = appointment_crud.get_appointments_with_details(db)
        return templates.TemplateResponse("appointments/index.html", {
            "request": request,
            "appointments": appointments,
            "title": "Appointment List"
        })
    except Exception as e:
        print(f"Error in appointment_list: {e}")
        return templates.TemplateResponse("appointments/index.html", {
            "request": request,
            "appointments": [],
            "title": "Appointment List",
            "error": str(e)
        })

@router.get("/today", response_class=HTMLResponse)
async def today_appointments(request: Request, db: Session = Depends(get_db)):
    """List today's appointments"""
    try:
        appointments = appointment_crud.get_today_appointments(db)
        return templates.TemplateResponse("appointments/today.html", {
            "request": request,
            "appointments": appointments,
            "title": "Today's Appointments",
            "today": date.today()
        })
    except Exception as e:
        print(f"Error in today_appointments: {e}")
        return templates.TemplateResponse("appointments/today.html", {
            "request": request,
            "appointments": [],
            "title": "Today's Appointments",
            "today": date.today(),
            "error": str(e)
        })

@router.get("/upcoming", response_class=HTMLResponse)
async def upcoming_appointments(request: Request, days: int = 7, db: Session = Depends(get_db)):
    """List upcoming appointments"""
    try:
        appointments = appointment_crud.get_upcoming_appointments(db, days)
        return templates.TemplateResponse("appointments/upcoming.html", {
            "request": request,
            "appointments": appointments,
            "days": days,
            "title": "Upcoming Appointments"
        })
    except Exception as e:
        print(f"Error in upcoming_appointments: {e}")
        return templates.TemplateResponse("appointments/upcoming.html", {
            "request": request,
            "appointments": [],
            "days": days,
            "title": "Upcoming Appointments",
            "error": str(e)
        })

@router.get("/patient/{patient_id}", response_class=HTMLResponse)
async def patient_appointments(request: Request, patient_id: int, db: Session = Depends(get_db)):
    """List appointments for a specific patient"""
    try:
        patient = patient_crud.get_patient(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        appointments = appointment_crud.get_appointments_by_patient(db, patient_id)
        return templates.TemplateResponse("appointments/patient_appointments.html", {
            "request": request,
            "patient": patient,
            "appointments": appointments,
            "title": f"Appointments - {patient.name}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in patient_appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/doctor/{doctor_id}", response_class=HTMLResponse)
async def doctor_appointments(request: Request, doctor_id: int, appointment_date: Optional[date] = None, db: Session = Depends(get_db)):
    """List appointments for a specific doctor"""
    try:
        doctor = doctor_crud.get_doctor(db, doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        appointments = appointment_crud.get_appointments_by_doctor(db, doctor_id, appointment_date)
        return templates.TemplateResponse("appointments/doctor_appointments.html", {
            "request": request,
            "doctor": doctor,
            "appointments": appointments,
            "selected_date": appointment_date or date.today(),
            "title": f"Appointments - Dr. {doctor.name}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in doctor_appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/add", response_class=HTMLResponse)
async def add_appointment_form(
    request: Request, 
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Show add appointment form"""
    try:
        # Get all patients, doctors, and staff directly
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        staff_members = db.query(Staff).all()
        
        selected_patient = None
        if patient_id:
            selected_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        selected_doctor = None
        if doctor_id:
            selected_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        return templates.TemplateResponse("appointments/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "staff_members": staff_members,
            "selected_patient": selected_patient,
            "selected_doctor": selected_doctor,
            "today": date.today().isoformat(),
            "title": "Add Appointment"
        })
    except Exception as e:
        print(f"ERROR in add_appointment_form: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a simple error page
        return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 50px; text-align: center; }}
                    .error {{ color: red; background: #ffeeee; padding: 20px; border-radius: 10px; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Error Loading Appointment Form</h1>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p><a href="/">Go to Home</a></p>
                </div>
            </body>
        </html>
        """, status_code=500)
    
@router.post("/add", response_class=HTMLResponse)
async def create_appointment(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    staff_id: Optional[int] = Form(None),
    appointment_date: date = Form(...),
    appointment_time: str = Form(...),
    reason: str = Form(...),
    symptoms: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    status: str = Form("scheduled"),
    follow_up_date: Optional[date] = Form(None),
    follow_up_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    try:
        # Parse time
        try:
            # Handle different time formats
            if ':' in appointment_time:
                # Split the time parts
                parts = appointment_time.split(':')
                if len(parts) >= 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    second = int(parts[2]) if len(parts) > 2 else 0
                    appointment_time_obj = time(hour, minute, second)
                else:
                    raise ValueError("Invalid time format")
            else:
                # If no colon, try to parse as HHMM
                if len(appointment_time) == 4:
                    hour = int(appointment_time[:2])
                    minute = int(appointment_time[2:])
                    appointment_time_obj = time(hour, minute)
                else:
                    raise ValueError("Invalid time format")
        except (ValueError, IndexError) as e:
            print(f"Time parsing error: {e}, received: {appointment_time}")
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/add.html", {
                "request": request,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "selected_patient": None,
                "selected_doctor": None,
                "error": f"Invalid time format: {appointment_time}. Please use HH:MM format.",
                "title": "Add Appointment",
                "today": date.today().isoformat()
            })
        
        # Validate doctor exists
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/add.html", {
                "request": request,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "error": "Doctor not found",
                "title": "Add Appointment",
                "today": date.today().isoformat()
            })
        
        # Validate patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/add.html", {
                "request": request,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "error": "Patient not found",
                "title": "Add Appointment",
                "today": date.today().isoformat()
            })
        
        # Check for conflicts
        if appointment_crud.check_appointment_conflict(db, doctor_id, appointment_date, appointment_time_obj):
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/add.html", {
                "request": request,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "error": "Doctor has a conflict at this time",
                "title": "Add Appointment",
                "today": date.today().isoformat()
            })
        
        # Create appointment data
        appointment_data = AppointmentCreate(
            patient_id=patient_id,
            doctor_id=doctor_id,
            staff_id=staff_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time_obj,
            reason=reason,
            symptoms=symptoms,
            notes=notes,
            status=status,
            follow_up_date=follow_up_date,
            follow_up_notes=follow_up_notes
        )
        
        # Create appointment
        appointment = appointment_crud.create_appointment(db, appointment_data)
        
        # 🔥 CHANGE HERE: Redirect to appointments list instead of view
        return RedirectResponse(url="/appointments", status_code=303)
    
    except Exception as e:
        print(f"ERROR in create_appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        staff_members = db.query(Staff).all()
        return templates.TemplateResponse("appointments/add.html", {
            "request": request,
            "patients": patients,
            "doctors": doctors,
            "staff_members": staff_members,
            "error": f"Error creating appointment: {str(e)}",
            "title": "Add Appointment",
            "today": date.today().isoformat()
        })

@router.get("/edit/{appointment_id}", response_class=HTMLResponse)
async def edit_appointment_form(request: Request, appointment_id: int, db: Session = Depends(get_db)):
    """Show edit appointment form"""
    try:
        appointment = appointment_crud.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        staff_members = db.query(Staff).all()
        
        return templates.TemplateResponse("appointments/edit.html", {
            "request": request,
            "appointment": appointment,
            "patients": patients,
            "doctors": doctors,
            "staff_members": staff_members,
            "title": f"Edit Appointment - {appointment.appointment_code}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in edit_appointment_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit/{appointment_id}")
async def update_appointment(
    request: Request,
    appointment_id: int,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    staff_id: Optional[int] = Form(None),
    appointment_date: date = Form(...),
    appointment_time: str = Form(...),
    reason: str = Form(...),
    symptoms: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    status: str = Form(...),
    follow_up_date: Optional[date] = Form(None),
    follow_up_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update appointment"""
    try:
        # Parse time
        try:
            if ':' in appointment_time:
                parts = appointment_time.split(':')
                if len(parts) >= 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    second = int(parts[2]) if len(parts) > 2 else 0
                    appointment_time_obj = time(hour, minute, second)
                else:
                    raise ValueError("Invalid time format")
            else:
                if len(appointment_time) == 4:
                    hour = int(appointment_time[:2])
                    minute = int(appointment_time[2:])
                    appointment_time_obj = time(hour, minute)
                else:
                    raise ValueError("Invalid time format")
        except (ValueError, IndexError) as e:
            appointment = appointment_crud.get_appointment(db, appointment_id)
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/edit.html", {
                "request": request,
                "appointment": appointment,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "error": f"Invalid time format: {appointment_time}",
                "title": "Edit Appointment"
            })
        
        # Check for conflicts (excluding current appointment)
        if appointment_crud.check_appointment_conflict(db, doctor_id, appointment_date, appointment_time_obj, appointment_id):
            appointment = appointment_crud.get_appointment(db, appointment_id)
            patients = db.query(Patient).all()
            doctors = db.query(Doctor).all()
            staff_members = db.query(Staff).all()
            return templates.TemplateResponse("appointments/edit.html", {
                "request": request,
                "appointment": appointment,
                "patients": patients,
                "doctors": doctors,
                "staff_members": staff_members,
                "error": "Doctor has a conflict at this time",
                "title": "Edit Appointment"
            })
        
        appointment_data = AppointmentUpdate(
            patient_id=patient_id,
            doctor_id=doctor_id,
            staff_id=staff_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time_obj,
            reason=reason,
            symptoms=symptoms,
            notes=notes,
            status=status,
            follow_up_date=follow_up_date,
            follow_up_notes=follow_up_notes
        )
        
        updated = appointment_crud.update_appointment(db, appointment_id, appointment_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # 🔥 CHANGE HERE: Redirect to appointments list instead of view
        return RedirectResponse(url="/appointments", status_code=303)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view/{appointment_id}", response_class=HTMLResponse)
async def view_appointment(request: Request, appointment_id: int, db: Session = Depends(get_db)):
    """View appointment details"""
    try:
        appointment = appointment_crud.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return templates.TemplateResponse("appointments/view.html", {
            "request": request,
            "appointment": appointment,
            "title": f"Appointment - {appointment.appointment_code}"
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in view_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-status/{appointment_id}")
async def update_appointment_status(
    appointment_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    try:
        appointment = appointment_crud.update_appointment_status(db, appointment_id, status)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # 🔥 CHANGE HERE: Redirect to appointments list instead of view
        return RedirectResponse(url="/appointments", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_appointment_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Delete appointment"""
    try:
        success = appointment_crud.delete_appointment(db, appointment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return RedirectResponse(url="/appointments", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API Routes
@router.get("/api", response_model=list)
async def api_get_appointments(
    skip: int = 0, 
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """API endpoint for appointments"""
    try:
        return appointment_crud.get_appointments(db, skip, limit, patient_id, doctor_id, status, date_from, date_to)
    except Exception as e:
        print(f"Error in api_get_appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/{appointment_id}")
async def api_get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Get single appointment via API"""
    try:
        appointment = appointment_crud.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_get_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api")
async def api_create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Create appointment via API"""
    try:
        # Check for conflicts
        if appointment_crud.check_appointment_conflict(db, appointment.doctor_id, appointment.appointment_date, appointment.appointment_time):
            raise HTTPException(status_code=409, detail="Doctor has a conflict at this time")
        return appointment_crud.create_appointment(db, appointment)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_create_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/{appointment_id}")
async def api_update_appointment(appointment_id: int, appointment: AppointmentUpdate, db: Session = Depends(get_db)):
    """Update appointment via API"""
    try:
        # Check for conflicts if doctor, date, or time changed
        if appointment.doctor_id or appointment.appointment_date or appointment.appointment_time:
            current = appointment_crud.get_appointment(db, appointment_id)
            if current:
                doctor_id = appointment.doctor_id or current.doctor_id
                appointment_date = appointment.appointment_date or current.appointment_date
                appointment_time = appointment.appointment_time or current.appointment_time
                if appointment_crud.check_appointment_conflict(db, doctor_id, appointment_date, appointment_time, appointment_id):
                    raise HTTPException(status_code=409, detail="Doctor has a conflict at this time")
        
        updated = appointment_crud.update_appointment(db, appointment_id, appointment)
        if not updated:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_update_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/{appointment_id}")
async def api_delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Delete appointment via API"""
    try:
        success = appointment_crud.delete_appointment(db, appointment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"message": "Appointment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_delete_appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/patient/{patient_id}")
async def api_get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    """Get all appointments for a patient via API"""
    try:
        return appointment_crud.get_appointments_by_patient(db, patient_id)
    except Exception as e:
        print(f"Error in api_get_patient_appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/doctor/{doctor_id}")
async def api_get_doctor_appointments(doctor_id: int, appointment_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Get all appointments for a doctor via API"""
    try:
        return appointment_crud.get_appointments_by_doctor(db, doctor_id, appointment_date)
    except Exception as e:
        print(f"Error in api_get_doctor_appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Debug Routes
@router.get("/test")
async def test_route(db: Session = Depends(get_db)):
    """Test route to check database connections"""
    try:
        patients = db.query(Patient).all()
        doctors = db.query(Doctor).all()
        staff = db.query(Staff).all()
        return {
            "status": "success", 
            "patient_count": len(patients),
            "doctor_count": len(doctors),
            "staff_count": len(staff)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/check-db")
async def check_database(db: Session = Depends(get_db)):
    """Check database tables and data"""
    try:
        patient_count = db.query(Patient).count()
        doctor_count = db.query(Doctor).count()
        staff_count = db.query(Staff).count()
        
        return {
            "patients": patient_count,
            "doctors": doctor_count,
            "staff": staff_count,
            "tables_exist": True
        }
    except Exception as e:
        return {"error": str(e)}