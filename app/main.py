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
from app.models.billing import Bill


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


# ================================================================
# HOME
# ================================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Hospital Management System</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                margin: 0;
                background: linear-gradient(135deg, #f4fbf8 0%, #e5f6f0 50%, #d2eee5 100%);
                padding: 50px 20px;
                text-align: center;
            }

            .container {
                max-width: 850px;
                margin: 0 auto;
                background: white;
                padding: 45px;
                border-radius: 9px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
            }

            h1 {
                color: #1a7f64;
                margin-bottom: 15px;
            }

            .status {
                color: #1a7f64;
                font-weight: 600;
                margin: 20px 0;
            }

            p {
                color: #64748b;
                line-height: 1.6;
            }

            .links {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 35px;
                flex-wrap: wrap;
            }

            .links a {
                display: inline-block;
                min-width: 140px;
                padding: 13px 25px;
                border-radius: 9px;
                text-decoration: none;
                color: white;
                font-weight: 600;
                font-size: 15px;
                box-shadow: 0 5px 15px rgba(26, 127, 100, 0.18);
                transition: all 0.25s ease;
            }

            .links a:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(26, 127, 100, 0.25);
            }

        </style>
    </head>

    <body>

        <div class="container">

            <h1>Hospital Management System</h1>

            <div class="status">
                Powered By Ali Ahmed
            </div>

            <p>
                Manage your hospital staff, patients,
                appointments, billing and prescriptions efficiently.
            </p>

            <div class="links">

                <a href="/dashboard"
                   style="background: linear-gradient(135deg, #1a7f64, #27ae8f);">
                    Dashboard
                </a>

                <a href="/doctors"
                   style="background: linear-gradient(135deg, #12664f, #1a7f64);">
                    Doctors
                </a>

                <a href="/patients"
                   style="background: linear-gradient(135deg, #17805f, #2bb673);">
                    Patients
                </a>

                <a href="/staff"
                   style="background: linear-gradient(135deg, #145a4a, #218c70);">
                    Staff
                </a>

                <a href="/appointments"
                   style="background: linear-gradient(135deg, #16745f, #35a88a);">
                    Appointments
                </a>

                <a href="/billing"
                   style="background: linear-gradient(135deg, #155c52, #249b83);">
                    Billing
                </a>

                <a href="/prescriptions"
                   style="background: linear-gradient(135deg, #0f6b58, #20a486);">
                    Prescriptions
                </a>

            </div>

        </div>

    </body>

    </html>
    """


# ================================================================
# DATABASE TEST
# ================================================================

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
    # 3. Total Revenue
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

    if not appointment_status:
        appointment_status = [
            ("No Appointments", 0)
        ]

    # --------------------------------
    # 5. Monthly Appointment Trends
    # --------------------------------

    monthly_data = []

    today = date.today()

    for i in range(5, -1, -1):

        month_date = today.replace(day=1)

        # Move backwards month by month
        for _ in range(i):
            month_date = (
                month_date - timedelta(days=1)
            ).replace(day=1)

        month_start = month_date

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
            "month": month_start.strftime("%b"),
            "count": count
        })

    # --------------------------------
    # 6. Additional Stats
    # --------------------------------

    total_bills = db.query(Bill).count()

    pending_bills = db.query(Bill).filter(
        Bill.payment_status == "unpaid"
    ).count()

    total_prescriptions = db.query(
        Prescription
    ).count()

    active_prescriptions = db.query(
        Prescription
    ).filter(
        Prescription.is_active == True
    ).count()

    # --------------------------------
    # Render Dashboard
    # --------------------------------

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,

            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_staff": total_staff,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "total_revenue": total_revenue,

            "appointment_status": appointment_status,
            "monthly_data": monthly_data,

            "total_bills": total_bills,
            "pending_bills": pending_bills,
            "total_prescriptions": total_prescriptions,
            "active_prescriptions": active_prescriptions,

            "today": today
        }
    )
