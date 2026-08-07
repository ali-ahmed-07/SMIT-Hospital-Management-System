# Hospital Management System

A professional web-based **Hospital Management System (HMS)** developed to manage hospital operations through a centralized and user-friendly platform. The system provides dedicated modules for Doctors, Patients, Staff, Prescriptions, Appointments, and Billing.

The application is designed to simplify hospital administration, maintain organized medical records, and provide efficient management of day-to-day hospital activities.

---

## Project Overview

The Hospital Management System provides a structured platform where hospital administrators and staff can manage important hospital records from a single system.

The system follows a modular architecture where each major hospital operation has its own dedicated management module.

### Main Modules

* Doctors Management
* Patients Management
* Staff Management
* Prescriptions Management
* Appointments Management
* Billing Management
* Dashboard
* Database Management

---

# Core Features

## 1. Doctors Management

The Doctors Management module is responsible for maintaining complete information about hospital doctors.

Administrators can create, view, update, and manage doctor records from a centralized interface.

### Features

* Create new doctor
* View doctor list
* View individual doctor details
* Edit doctor information
* Delete doctor record
* Manage doctor information
* Assign doctor-related information to patients and appointments
* Search and manage doctors

### Doctor Information

A doctor record can contain information such as:

* Doctor Code
* Doctor Name
* Specialization
* Qualification
* Gender
* Phone Number
* Email
* Address
* Joining Date
* Department
* Status
* Additional Information

### CRUD Operations

| Operation | Description                      |
| --------- | -------------------------------- |
| Create    | Add a new doctor                 |
| Read      | View doctor list and details     |
| Update    | Edit existing doctor information |
| Delete    | Remove doctor record             |

---

# 2. Patients Management

The Patients Management module is used to maintain complete patient records.

This module allows hospital staff to register patients and manage their medical and personal information.

### Features

* Create new patient
* View patient list
* View patient details
* Edit patient information
* Delete patient record
* Assign doctor
* Manage admission information
* Manage discharge information
* Maintain patient contact information
* Search patients

### Patient Information

Patient records can include:

* Patient Code
* Patient Name
* Age
* Gender
* Phone Number
* Address
* Disease
* Assigned Doctor
* Admission Date
* Discharge Date
* Patient Status
* Additional Information

### CRUD Operations

| Operation | Description                |
| --------- | -------------------------- |
| Create    | Register a new patient     |
| Read      | View patient records       |
| Update    | Modify patient information |
| Delete    | Remove patient record      |

---

# 3. Staff Management

The Staff Management module is designed to manage hospital employees and staff members.

It provides a centralized location for maintaining staff information and their roles within the hospital.

### Features

* Add new staff member
* View staff list
* View staff details
* Edit staff information
* Delete staff record
* Manage staff designation
* Manage staff department
* Manage staff contact information
* Manage employment status

### Staff Information

A staff record can include:

* Staff Code
* Staff Name
* Designation
* Department
* Gender
* Phone Number
* Email
* Address
* Joining Date
* Status
* Additional Information

### CRUD Operations

| Operation | Description            |
| --------- | ---------------------- |
| Create    | Add new staff member   |
| Read      | View staff records     |
| Update    | Edit staff information |
| Delete    | Remove staff record    |

---

# 4. Prescriptions Management

The Prescriptions Management module is used to manage prescriptions issued to patients by doctors.

This module connects patients and doctors and allows medical prescription records to be maintained systematically.

### Features

* Create prescription
* View prescription list
* View prescription details
* Edit prescription
* Delete prescription
* Assign prescription to patient
* Assign prescription to doctor
* Add prescription details
* Manage prescription status
* Track prescription dates

### Prescription Information

A prescription may contain:

* Prescription Code
* Patient
* Doctor
* Prescription Date
* Medicine
* Dosage
* Frequency
* Duration
* Instructions
* Notes
* Status

### CRUD Operations

| Operation | Description                    |
| --------- | ------------------------------ |
| Create    | Create a new prescription      |
| Read      | View prescription list/details |
| Update    | Modify prescription            |
| Delete    | Remove prescription            |

---

# 5. Appointments Management

The Appointments Management module handles appointments between patients and doctors.

It helps hospital staff organize scheduled visits and maintain appointment records.

### Features

* Create appointment
* View appointment list
* View appointment details
* Edit appointment
* Delete appointment
* Assign patient
* Assign doctor
* Set appointment date
* Set appointment time
* Manage appointment status
* Add appointment notes

### Appointment Information

An appointment can contain:

* Appointment Code
* Patient
* Doctor
* Appointment Date
* Appointment Time
* Reason
* Notes
* Status

### Appointment Status

Typical appointment statuses include:

* Scheduled
* Confirmed
* Completed
* Cancelled
* Rescheduled

### CRUD Operations

| Operation | Description                |
| --------- | -------------------------- |
| Create    | Schedule a new appointment |
| Read      | View appointments          |
| Update    | Modify appointment         |
| Delete    | Remove appointment         |

---

# 6. Billing Management

The Billing Management module is responsible for managing patient billing and payment records.

It allows hospital staff to create bills, track charges, and maintain payment information.

### Features

* Create new bill
* View billing list
* View bill details
* Edit billing information
* Delete bill
* Assign bill to patient
* Add services and charges
* Calculate total amount
* Manage paid amount
* Manage remaining amount
* Manage payment status
* Track billing date

### Billing Information

A billing record may contain:

* Bill Number
* Patient
* Billing Date
* Service Description
* Quantity
* Unit Price
* Total Amount
* Discount
* Paid Amount
* Remaining Amount
* Payment Method
* Payment Status
* Notes

### Payment Status

* Paid
* Partially Paid
* Pending
* Cancelled

### CRUD Operations

| Operation | Description              |
| --------- | ------------------------ |
| Create    | Create a new bill        |
| Read      | View billing records     |
| Update    | Edit billing information |
| Delete    | Remove billing record    |

---

# 7. Dashboard

The Dashboard provides an overview of the hospital management system.

It allows administrators to quickly understand the current status of hospital operations.

### Dashboard Statistics

The dashboard can display:

* Total Doctors
* Total Patients
* Total Staff
* Total Prescriptions
* Total Appointments
* Total Bills
* Pending Appointments
* Completed Appointments
* Pending Payments
* Recent Patients
* Recent Appointments
* Recent Prescriptions

The dashboard acts as the central starting point for accessing different hospital modules.

---

# Module Architecture

Each major module follows a consistent management structure.

For example, the Doctors module follows:

**Doctors → Create → List → View → Edit → Delete**

The same management pattern is implemented for other major modules.

### Standard Module Flow

```text
Create
   ↓
Store Record
   ↓
List Records
   ↓
View Details
   ↓
Edit Record
   ↓
Update Record
   ↓
Delete Record
```

This structure provides consistency throughout the application and makes the system easier to maintain and use.

---

# CRUD Implementation

The Hospital Management System uses CRUD operations for managing database records.

CRUD stands for:

### Create

Used to create a new record.

Example:

```text
Create Doctor
Create Patient
Create Staff
Create Prescription
Create Appointment
Create Bill
```

### Read

Used to retrieve and display existing records.

Example:

```text
Doctor List
Patient List
Staff List
Prescription List
Appointment List
Billing List
```

### Update

Used to modify an existing record.

Example:

```text
Edit Doctor
Edit Patient
Edit Staff
Edit Prescription
Edit Appointment
Edit Bill
```

### Delete

Used to remove an existing record from the system.

Example:

```text
Delete Doctor
Delete Patient
Delete Staff
Delete Prescription
Delete Appointment
Delete Bill
```

---

# Module Summary

| Module        | Create | List | View | Edit | Delete |
| ------------- | :----: | :--: | :--: | :--: | :----: |
| Doctors       |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |
| Patients      |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |
| Staff         |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |
| Prescriptions |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |
| Appointments  |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |
| Billing       |    ✓   |   ✓  |   ✓  |   ✓  |    ✓   |

---

# Technology Stack

The project is developed using modern web development technologies.

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates
* Bootstrap / Custom CSS

### Database

* MySQL / MariaDB
* phpMyAdmin

### Development Tools

* Visual Studio Code
* Git
* GitHub
* Python Virtual Environment

---

# Project Structure

A typical project structure is organized as follows:

```text
Hospital-Management-System/
│
├── app/
│   ├── models/
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── staff.py
│   │   ├── prescription.py
│   │   ├── appointment.py
│   │   └── billing.py
│   │
│   ├── routes/
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   ├── staff.py
│   │   ├── prescriptions.py
│   │   ├── appointments.py
│   │   └── billing.py
│   │
│   ├── schemas/
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── staff.py
│   │   ├── prescription.py
│   │   ├── appointment.py
│   │   └── billing.py
│   │
│   ├── templates/
│   │   ├── doctors/
│   │   ├── patients/
│   │   ├── staff/
│   │   ├── prescriptions/
│   │   ├── appointments/
│   │   └── billing/
│   │
│   ├── database.py
│   └── main.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Database Relationships

The system is designed around relationships between major hospital entities.

```text
Doctor
   │
   ├───────────────┐
   │               │
   ▼               ▼
Patient        Appointment
   │               │
   ▼               ▼
Prescription     Doctor
   │
   ▼
Billing
```

### Main Relationships

* A doctor can have multiple patients.
* A patient can have multiple appointments.
* A doctor can have multiple appointments.
* A patient can have multiple prescriptions.
* A doctor can issue multiple prescriptions.
* A patient can have multiple billing records.
* Appointments connect doctors with patients.
* Prescriptions connect doctors with patients.

These relationships allow the system to maintain connected and organized hospital data.

---

# Application Workflow

A typical hospital workflow can be represented as:

```text
Doctor Registration
        ↓
Patient Registration
        ↓
Appointment Scheduling
        ↓
Doctor Consultation
        ↓
Prescription Creation
        ↓
Billing
        ↓
Payment
        ↓
Record Management
```

This workflow provides a complete basic cycle for managing hospital operations.

---

# User Interface

The system provides dedicated interfaces for each module.

Each module contains:

* Page Header
* Add/Create Button
* Search / Filter
* Data Table
* View Action
* Edit Action
* Delete Action
* Form Validation
* Status Indicators
* Navigation Controls

The interface follows a consistent design so users do not have to relearn the system every time they click another module. Humanity has suffered enough from inconsistent admin panels.

---

# Validation and Data Management

The system validates important information before storing records in the database.

Examples include:

* Required field validation
* Valid phone number format
* Valid email format
* Date validation
* Numeric field validation
* Foreign-key relationship validation
* Status validation
* Duplicate record prevention where required

This helps maintain data accuracy and database integrity.

---

# Error Handling

The application handles common errors such as:

* Invalid record ID
* Missing records
* Invalid form data
* Database errors
* Duplicate records
* Invalid relationships
* Unauthorized operations

Appropriate error messages are provided to help users understand and resolve problems.

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/ali-ahmed-07/SMIT-Hospital-Management-System.git
```

## 2. Navigate to Project

```bash
cd SMIT-Hospital-Management-System
```

## 3. Create Virtual Environment

```bash
python -m venv venv
```

## 4. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure Database

Create a MySQL/MariaDB database and configure the database connection according to the project's environment configuration.

Example:

```text
Database: hospital_db
Host: localhost
User: root
Password: your_password
```

## 7. Run Application

```bash
uvicorn app.main:app --reload
```

The application will then be available through the local development server.

---

# Future Enhancements

The system can be extended with additional features such as:

* User Authentication
* Role-Based Access Control
* Admin Management
* Department Management
* Medicine Management
* Pharmacy Management
* Laboratory Management
* Medical Reports
* Patient Medical History
* Doctor Availability
* Appointment Calendar
* Invoice Printing
* PDF Reports
* Email Notifications
* SMS Notifications
* Advanced Search
* Reporting and Analytics
* Audit Logs

---

# Project Goals

The primary goals of the Hospital Management System are:

1. Digitize hospital records.
2. Reduce manual record keeping.
3. Improve patient information management.
4. Simplify doctor and staff management.
5. Organize appointments efficiently.
6. Maintain prescription records.
7. Simplify billing operations.
8. Provide centralized access to hospital information.
9. Improve data accuracy.
10. Provide a scalable foundation for future hospital modules.

---

# Conclusion

The Hospital Management System provides a centralized solution for managing essential hospital operations.

With dedicated CRUD-based modules for **Doctors, Patients, Staff, Prescriptions, Appointments, and Billing**, the system provides a structured foundation for managing hospital data efficiently.

The modular architecture makes the application easier to maintain, extend, and integrate with additional healthcare-related functionality in the future.

---

## License

This project is developed for educational and project development purposes.

---

## Author

**Ali Ahmed**

Hospital Management System
Built with **Python, FastAPI, SQLAlchemy, HTML, CSS, JavaScript, and MySQL/MariaDB**.
