# Accounts Payable Automation System with OCR

## Overview

The Accounts Payable (AP) Automation System with OCR is an enterprise-grade web application designed to digitize, extract, and automate the validation of vendor invoices. 

**Business Problem:** Manual invoice processing is slow, error-prone, and resource-intensive. Finance teams spend countless hours doing data entry, manually validating line items against purchase orders, and routing physical or PDF invoices for manager approvals.
**Why AP Automation Matters:** Digitizing this workflow eliminates data entry errors, drastically reduces turnaround time, prevents duplicate payments, and provides real-time cash flow visibility for treasury forecasting.
**Project Goals & Benefits:** The primary goal of this system is to serve as a high-efficiency pre-accounting engine. It uses AI (OCR) to extract data instantly, enforces rigid mathematical and business validation rules, automates Purchase Order (PO) matching, and provides a unified approval pipeline with full audit traceability.

---

## Features

### Implemented Features

* **Invoice Capture:** Supports manual upload of PDF, PNG, and JPG invoices through a drag-and-drop interface.
* **OCR & AI Extraction:** Integrates with Gemini AI (with Mistral fallback capability) to instantly extract invoice headers (Vendor Name, Date, Invoice Number, Total, GST) and granular line items.
* **Validation Engine:** Automatically checks for mandatory fields, verifies tax totals against line items, and flags discrepancies.
* **PO Matching:** Supports automated 2-Way and 3-Way matching. Users can link an invoice to a PO to verify quantities and unit prices, with visual flags for mismatches.
* **Approval Workflow:** A linear, role-based approval queue. Approvers can review extracted data, PO matches, and line items, then digitally approve or reject invoices with mandatory comments.
* **Vendor Management:** A basic vendor master ledger tracking Vendor IDs, names, and GSTINs.
* **Dashboard:** A real-time command center displaying total open invoices, approval bottlenecks, validation failure rates, and AI OCR confidence scores (Note: OCR confidence is currently a 95% placeholder, not probabilistic).
* **Reports:** Analytical views including AP Aging (30/60/90 days), Exception Reports, Invoice Status pipelines, and fully paginated, filterable Audit Logs.
* **Security & RBAC:** Role-Based Access Control (Admin, Approver, Finance) utilizing JWT authentication. Restricts approval actions to authorized users and logs every action to an immutable audit ledger.

### Partially / Not Implemented Features
* **Payment Processing:** Banking integration and automated disbursements are not yet implemented. Invoices halt at the `APPROVED` state.
* **Bulk Upload / Email Ingestion:** The system currently processes invoices one at a time via the UI.
* **External GST Verification:** GSTINs are structurally validated via RegEx, but not verified against live government tax portals.

---

## Architecture

```mermaid
graph TD
    subgraph Frontend [React SPA]
        UI[Dashboard / UI Components]
        API_Client[Axios Client]
    end

    subgraph Backend [FastAPI Server]
        Auth[JWT Middleware]
        Routers[API Endpoints]
        Services[Business Logic & Validation]
        ORM[SQLAlchemy]
    end

    subgraph External [AI OCR Layer]
        Gemini[Google Gemini API]
        Mistral[Mistral API Fallback]
    end

    subgraph Database [PostgreSQL]
        DB[(Relational Schema)]
    end

    UI --> API_Client
    API_Client -->|REST| Auth
    Auth --> Routers
    Routers --> Services
    Services -->|Extract Data| Gemini
    Services -.->|Fallback| Mistral
    Services --> ORM
    ORM --> DB
```

---

## Workflow Diagram

```mermaid
flowchart TD
    A[Invoice Upload] --> B[OCR & AI Extraction]
    B --> C{Validation Engine}
    C -- Errors Found --> D[Validation Failed]
    C -- Clean Data --> E[PO Matching]
    E --> F[Approval Queue]
    F --> G{Manager Review}
    G -- Approved --> H[Ready for Payment]
    G -- Rejected --> I[Rejected]
    
    H -.-> J[Audit Logs & Reports]
    I -.-> J
    D -.-> J
```

---

## Technology Stack

* **Frontend:** React, TypeScript, Vite, Tailwind-like custom CSS (Lucide Icons).
* **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
* **Database:** PostgreSQL (Relational Data & Audit Ledgers).
* **OCR:** Google Gemini 1.5 Flash (Primary) / Mistral (Fallback).
* **Authentication:** OAuth2 with Password Flow (JWT Bearer Tokens).

---

## Setup Instructions

### Database Setup
1. Install PostgreSQL and create a database named `ap_automation`.
2. Ensure the database user has full schema privileges.

### Backend Setup
1. Navigate to the `backend/` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `alembic upgrade head`
6. Seed the database (optional): `python seed_users.py` & `python seed_vendors.py`
7. Start the server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to the `frontend/` directory.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

### Environment Variables
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ap_automation
SECRET_KEY=your_super_secret_jwt_key
GEMINI_API_KEY=your_google_gemini_key
```

---

## Demo Credentials

The repository includes a seeding script (`backend/seed_users.py`) that generates the following default credentials for testing RBAC:

* **Admin:** `admin@example.com` / `password123`
* **Approver:** `approver@example.com` / `password123`
* **Finance:** `finance@example.com` / `password123`


## Module Coverage Summary

| Module | Status | Notes |
| :--- | :--- | :--- |
| **Invoice Capture** | Implemented | Manual UI upload only. |
| **OCR & AI Extraction** | Implemented | Gemini integration successful. |
| **Validation Engine** | Implemented | Math and mandatory fields enforced. |
| **PO Matching** | Implemented | 2-Way and 3-Way match logic functional. |
| **Approval Workflow** | Implemented | Linear role-based approvals. |
| **Vendor Management** | Implemented | Basic CRUD and ledger. |
| **Dashboard** | Partial | Missing turnaround time analytics. *Note: OCR confidence metric is currently a hardcoded 95% placeholder.* |
| **Reports** | Partial | AP Aging, Invoice Status, and Exceptions built. |
| **Payment Processing**|  Not Implemented | Deferred to Phase 2. |

---

## Future Enhancements

Please refer to the [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) document for a detailed breakdown of current technical constraints and the future feature roadmap.
