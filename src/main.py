from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import register_exception_handlers
from src.router import matchmaking_router
from src.router.embeddings import router as embeddings_router
from src.router.vectors import router as vectors_router

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
app.include_router(matchmaking_router)
app.include_router(embeddings_router)
app.include_router(vectors_router)

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios externos al arrancar"""
    from src.infrastructure.external.openai_client import init_openai_client
    from src.infrastructure.external.pinecone_client import init_pinecone_client
    from src.infrastructure.schema.embedding import ClientConfig
    from src.infrastructure.config import config as infra_config
    
    # Inicializar OpenAI
    openai_config = ClientConfig(api_key=infra_config.OPENAI_API_KEY)
    init_openai_client(openai_config)
    
    # Inicializar Pinecone
    init_pinecone_client()
    
    print("✅ Servicios externos inicializados")

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
