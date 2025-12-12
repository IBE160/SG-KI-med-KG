from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.suggestions import router as suggestions_router
from app.api.v1.endpoints.audit_logs import router as audit_logs_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.assessments import router as assessments_router
from app.api.v1.endpoints.mapping import router as mapping_router
from app.api.v1.endpoints.reports import router as reports_router
from app.config import settings
from app.routes.compliance import router as compliance_router
from app.routes.items import router as items_router

from .schemas import UserCreate, UserRead, UserUpdate
from .users import AUTH_URL_PATH, auth_backend, fastapi_users
from .utils import simple_generate_unique_route_id

app = FastAPI(
    generate_unique_id_function=simple_generate_unique_route_id,
    openapi_url=settings.OPENAPI_URL,
)

# Middleware for CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user management routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=f"/{AUTH_URL_PATH}/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include items routes
app.include_router(items_router, prefix="/items")
app.include_router(compliance_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(suggestions_router, prefix="/api/v1/suggestions", tags=["suggestions"])
app.include_router(audit_logs_router, prefix="/api/v1/audit-logs", tags=["audit-logs"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(assessments_router, prefix="/api/v1/assessments", tags=["assessments"])
app.include_router(mapping_router, prefix="/api/v1/mappings", tags=["mappings"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])

add_pagination(app)
