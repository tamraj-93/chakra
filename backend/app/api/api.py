from fastapi import APIRouter

from app.api.endpoints import users, consultation, templates, auth, analytics, consultation_templates, template_generator, documents, healthcare_rag, healthcare_formatter, healthcare_templates, healthcare_consultation

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(consultation.router)
api_router.include_router(templates.router)
api_router.include_router(analytics.router)
api_router.include_router(consultation_templates.router, tags=["consultation-templates"])
api_router.include_router(template_generator.router)
api_router.include_router(documents.router, prefix="/v1/documents", tags=["documents"])
api_router.include_router(healthcare_rag.router, prefix="/v1/healthcare-rag", tags=["healthcare-rag"])
api_router.include_router(healthcare_formatter.router, prefix="/v1/healthcare-formatter", tags=["healthcare-formatter"])
api_router.include_router(healthcare_templates.router, prefix="/v1/healthcare-templates", tags=["healthcare-templates"])
api_router.include_router(healthcare_consultation.router, prefix="/v1/healthcare-consultation", tags=["healthcare-consultation"])