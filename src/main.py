from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers
from src.routers import matchmaking_router

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

# Registrar routers
app.include_router(matchmaking_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
