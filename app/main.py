from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from datetime import date, timedelta

from app.database import engine, get_db, Base

from app.routes import (
    doctors,
    patients,
    staff,
    prescriptions,
    appointments,
    billing
)

# Models
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.staff import Staff
from app.models.prescription import Prescription
from app.models.appointment import Appointment
from app.models.billing import Bill, BillItem


def create_tables():
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hospital Management System",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# Templates
templates = Jinja2Templates(
    directory="app/templates"
)


# Include Routers
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(staff.router)
app.include_router(prescriptions.router)
app.include_router(appointments.router)
app.include_router(billing.router)


# Startup
@app.on_event("startup")
async def startup():
    create_tables()
    print("Database tables created successfully!")


# Home
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hospital Management System</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 50px;
                text-align: center;
                background: #f5f7fa;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                color: #2c3e50;
            }

            .btn {
                display: inline-block;
                padding: 12px 30px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }

            .btn:hover {
                background: #2980b9;
            }

            .status {
                color: #27ae60;
                margin: 20px 0;
            }

            .links {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }

            .links a {
                padding: 12px 30px;
                border-radius: 5px;
                text-decoration: none;
            }

            .btn-doctor {
                background: #3498db;
                color: white;
            }

            .btn-patient {
                background: #2ecc71;
                color: white;
            }

            .btn-staff {
                background: #9b59b6;
                color: white;
            }

            .btn-prescription {
                background: #e67e22;
                color: white;
            }

            .btn-dashboard {
                background: #1a7f64;
                color: white;
            }

            .btn-dashboard:hover {
                background: #136b53;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>🏥 Hospital Management System</h1>

            <div class="status">
                ✅ System is Running
            </div>

            <p>
                Manage your hospital staff, patients,
                appointments, billing and prescriptions efficiently
            </p>

            <div class="links">

                <a href="/doctors" class="btn-doctor">
                    👨‍⚕️ Doctors
                </a>

                <a href="/patients" class="btn-patient">
                    👥 Patients
                </a>

                <a href="/staff" class="btn-staff">
                    👔 Staff
                </a>

                <a href="/appointments" class="btn" style="background:#e67e22;">
                    📅 Appointments
                </a>

                <a href="/billing" class="btn" style="background:#8e44ad;">
                    💰 Billing
                </a>

                <a href="/prescriptions" class="btn-prescription">
                    💊 Prescriptions
                </a>

                <a href="/dashboard" class="btn-dashboard">
                    📊 Dashboard
                </a>

            </div>

        </div>

    </body>
    </html>
    """


# Database Test
@app.get("/db-test")
def db_test():

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "Database Connected Successfully"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ================================================================
# DASHBOARD
# ================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    # --------------------------------
    # 1. Basic Counts
    # --------------------------------

    total_doctors = db.query(Doctor).count()
    total_patients = db.query(Patient).count()
    total_staff = db.query(Staff).count()
    total_appointments = db.query(Appointment).count()

    # --------------------------------
    # 2. Today's Appointments
    # --------------------------------

    today = date.today()

    today_appointments = db.query(Appointment).filter(
        Appointment.appointment_date == today
    ).count()

    # --------------------------------
    # 3. Total Revenue (Paid Bills)
    # --------------------------------

    total_revenue = db.query(
        func.sum(Bill.total_amount)
    ).filter(
        Bill.payment_status == "paid"
    ).scalar() or 0

    # --------------------------------
    # 4. Appointment Status Distribution
    # --------------------------------

    appointment_status = db.query(
        Appointment.status,
        func.count(Appointment.id)
    ).filter(
        Appointment.status.isnot(None)
    ).group_by(
        Appointment.status
    ).all()

    # Agar koi data nahi hai toh default show karein
    if not appointment_status:
        appointment_status = [('No Appointments', 0)]

    # --------------------------------
    # 5. Monthly Appointment Trends (Last 6 Months)
    # --------------------------------

    monthly_data = []
    today = date.today()

    for i in range(5, -1, -1):
        # Month calculation
        month_date = today.replace(day=1)
        month_date = month_date - timedelta(days=30 * i)

        month_start = month_date.replace(day=1)

        if month_date.month == 12:
            month_end = month_date.replace(
                year=month_date.year + 1,
                month=1,
                day=1
            ) - timedelta(days=1)
        else:
            month_end = month_date.replace(
                month=month_date.month + 1,
                day=1
            ) - timedelta(days=1)

        count = db.query(Appointment).filter(
            Appointment.appointment_date >= month_start,
            Appointment.appointment_date <= month_end
        ).count()

        monthly_data.append({
            'month': month_start.strftime('%b'),
            'count': count
        })

    # --------------------------------
    # 6. Additional Stats (Optional)
    # --------------------------------

    # Total Bills
    total_bills = db.query(Bill).count()

    # Pending Bills
    pending_bills = db.query(Bill).filter(
        Bill.payment_status == 'unpaid'
    ).count()

    # Total Prescriptions
    total_prescriptions = db.query(Prescription).count()

    # Active Prescriptions
    active_prescriptions = db.query(Prescription).filter(
        Prescription.is_active == True
    ).count()

    # --------------------------------
    # Render Dashboard Template
    # --------------------------------

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,

            # Stats
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_staff": total_staff,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "total_revenue": total_revenue,

            # Charts Data
            "appointment_status": appointment_status,
            "monthly_data": monthly_data,

            # Extra Stats
            "total_bills": total_bills,
            "pending_bills": pending_bills,
            "total_prescriptions": total_prescriptions,
            "active_prescriptions": active_prescriptions,

            # Date
            "today": today
        }
    )