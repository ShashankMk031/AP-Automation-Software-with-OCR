# AP Automation System - Deployment Checklist

This document provides a comprehensive, step-by-step checklist to ensure a safe and verified deployment of the Accounts Payable Automation software into a production environment.

## Phase 1: Pre-Deployment Verification

### 1. Environment & Infrastructure
- [ ] **Infrastructure Provisioning**: Verify production instances (VMs, containers, or PaaS environments) are provisioned for both the frontend (Node.js/Nginx) and backend (Python/Uvicorn).
- [ ] **Database Connection**: Ensure the production PostgreSQL database is accessible and the connection string is correctly formatted as `DATABASE_URL`.
- [ ] **Secrets Management**: 
  - [ ] Generate a cryptographically secure `SECRET_KEY` for JWT signing.
  - [ ] Set `GEMINI_API_KEY` (and optionally `MISTRAL_API_KEY`).
  - [ ] Ensure `.env` is loaded by the production environment and NOT committed to the repository.

### 2. Codebase & Repository
- [ ] **Dependency Audit**: Verify `backend/requirements.txt` is complete.
- [ ] **Build Validation**: Execute `npm run build` locally in the `frontend` directory to ensure there are no TypeScript or bundling errors.
- [ ] **Repository Hygiene**: Verify `.gitignore` is intact, ensuring no `.pyc`, `.env`, or local `venv` directories are pushed.

## Phase 2: Deployment Execution

### 1. Database Migrations
- [ ] **Run Alembic Migrations**: Connect to the production database and execute `alembic upgrade head` to generate all tables and constraints (`users`, `vendors`, `purchase_orders`, `grns`, `invoices`, `invoice_line_items`, `audit_logs`).
- [ ] **Seed Initial Data**: (Optional but recommended) Run a modified data seeding script to create the initial production `ADMIN` user account. Do NOT seed test invoices or dummy vendors in production.

### 2. Backend Deployment
- [ ] **Start Uvicorn**: Launch the backend API using a production ASGI server configuration (e.g., `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`).
- [ ] **CORS Configuration**: Verify that `backend/app/main.py` has the CORS middleware configured to explicitly allow the production frontend domain (e.g., `https://ap-automation.company.com`).

### 3. Frontend Deployment
- [ ] **Configure API Client**: Ensure the frontend's `VITE_API_URL` environment variable points to the production backend URL (e.g., `https://api.ap-automation.company.com/api/v1`).
- [ ] **Deploy Build Artifacts**: Serve the `frontend/dist` directory using a production web server (Nginx, Apache, or a CDN like Vercel/Netlify).

## Phase 3: Post-Deployment Verification

Perform these functional tests immediately after deployment to verify system integrity:

### 1. Authentication & RBAC
- [ ] Log in as an `ADMIN` and verify access to the Dashboard.
- [ ] Attempt to access the Approval Queue as an `ADMIN` (Should show Access Denied / restrictions).
- [ ] Log in as an `APPROVER` and verify Approval Queue access.

### 2. Invoice Capture & OCR
- [ ] Upload a standard vendor invoice PDF.
- [ ] Verify the OCR engine successfully extracts the Vendor Name, Invoice Number, Subtotal, Tax, and Line Items.
- [ ] Verify the system correctly flags any math discrepancies.

### 3. PO Matching Workflow
- [ ] Create a test Purchase Order directly in the database (or via backend routes).
- [ ] Run a PO Match against the uploaded invoice.
- [ ] Verify it correctly returns `MATCHED` or `MISMATCH`.

### 4. Approval Routing
- [ ] Log in as an `APPROVER`.
- [ ] Add a mandatory comment and click **Approve**.
- [ ] Verify the Invoice Status updates to `APPROVED` and the action is recorded in the Audit Log.

### 5. Reporting
- [ ] Navigate to the Dashboard. Verify the KPI cards load correctly.
- [ ] Navigate to the AP Aging Report. Verify data renders without 500 errors.
- [ ] Navigate to the Audit Log. Verify all previous test actions were accurately logged with timestamps.

## Phase 4: Sign-Off
- [ ] Review application logs for any hidden exceptions or OCR rate-limit warnings.
- [ ] Perform a final database backup check.
- [ ] **Go-Live Complete**.
