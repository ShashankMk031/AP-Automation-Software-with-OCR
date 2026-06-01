from fastapi import APIRouter
from app.api.endpoints import health, auth, vendors, invoices

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
