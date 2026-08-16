from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.prediction import router as prediction_router
from app.api.assessment import router as assessment_router
from app.api.records import router as records_router
from app.api.knowledge import router as knowledge_router
from app.api.research import router as research_router
from app.api.patients import router as patients_router
from app.api.ai import router as ai_router
from app.api.hospitals import router as hospitals_router
from app.api.emergency import router as emergency_router
from app.api.emergency_contacts import router as emergency_contacts_router
from app.api.auth import router as auth_router


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    (b"cache-control", b"no-store"),
                ]

                existing = {k.lower() for k, _ in headers}

                for key, value in security_headers:
                    if key not in existing:
                        headers.append((key, value))

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


app = FastAPI(
    title="Aegis Health AI",
    description="Evidence-first health intelligence prototype.",
    version="0.9.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SecurityHeadersMiddleware)


app.include_router(prediction_router)
app.include_router(assessment_router)
app.include_router(records_router)
app.include_router(knowledge_router)
app.include_router(research_router)
app.include_router(patients_router)
app.include_router(ai_router)
app.include_router(hospitals_router)
app.include_router(emergency_router)
app.include_router(emergency_contacts_router)
app.include_router(auth_router)


@app.get("/")
def root():

    return {
        "name": "Aegis Health AI",
        "status": "online",
        "version": "0.9.0",
        "principle": "No evidence, no conclusion."
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }






app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "127.0.0.1",
        "localhost",
    ],
)


