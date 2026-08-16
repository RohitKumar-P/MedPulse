from fastapi import FastAPI

app = FastAPI(
    title="Aegis Health AI",
    description="AI-powered early health risk assessment platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "name": "Aegis Health AI",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }