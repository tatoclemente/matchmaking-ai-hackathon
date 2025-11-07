from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import register_exception_handlers
from src.routers import example

app = FastAPI(
    title="PADER Matchmaking AI",
    description="Microservicio de matchmaking con IA para PADER",
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

# Registrar exception handlers globales
register_exception_handlers(app)

# Registrar routers
app.include_router(example.router)

@app.get("/")
async def root():
    return {
        "message": "PADER Matchmaking AI - Hackathon 2025",
        "status": "ready",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "matchmaking-ai",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
