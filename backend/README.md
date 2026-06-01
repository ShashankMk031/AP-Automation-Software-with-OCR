# Accounts Payable Automation System - Backend

## Tech Stack
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pydantic
- JWT Authentication
- Python 3.12

## Local Setup

1. **Create and activate a virtual environment:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment Variables:**
Copy `.env.example` to `.env` and configure your database settings:
```bash
cp .env.example .env
```

4. **Database Setup:**
Ensure PostgreSQL is running and you have created the database specified in `.env` (default is `accounts_payable`).

5. **Run Migrations:**
```bash
cd backend
alembic upgrade head
```
*(To generate a new migration after modifying models, run: `alembic revision --autogenerate -m "description"`)*

6. **Run the Application:**
```bash
cd backend
uvicorn app.main:app --reload
```

## API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`
