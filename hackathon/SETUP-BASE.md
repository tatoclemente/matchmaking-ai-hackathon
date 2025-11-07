# 🔧 SETUP BASE - Repo Listo para Hackathon

Este documento describe cómo preparar el repositorio base con todo configurado para que el día de la hackathon solo sea `docker-compose up` y empezar a codear.

---

## 📁 Estructura de Archivos a Crear

```
matchmaking-ai/
├── docker-compose.yml          # PostgreSQL + FastAPI
├── Dockerfile                  # FastAPI container
├── requirements.txt            # Python dependencies
├── .env.example               # Template de variables
├── .gitignore                 # Ignorar .env, venv, etc.
├── README.md                  # Instrucciones básicas
├── init.sql                   # Script para crear tabla players
│
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI app básica
│   ├── config.py              # Cargar env vars
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── external/
│   │   └── __init__.py
│   │
│   ├── database/
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   └── __init__.py
│   │
│   ├── seeders/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
└── tests/
    └── __init__.py
```

---

## 📄 Contenido de Cada Archivo

### 1. `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto
EXPOSE 8000

# Comando para desarrollo (con reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 2. `docker-compose.yml`
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: matchmaking_db
    environment:
      POSTGRES_USER: pader
      POSTGRES_PASSWORD: pader123
      POSTGRES_DB: matchmaking
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pader"]
      interval: 5s
      timeout: 5s
      retries: 5

  # FastAPI Application
  api:
    build: .
    container_name: matchmaking_api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pader:pader123@postgres:5432/matchmaking
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME}
      - PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
    volumes:
      - ./src:/app/src  # Hot reload
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. `requirements.txt`
```txt
fastapi[standard]==0.121.0
openai==2.7.1
pinecone==7.3.0
numpy==2.2.3
pandas==2.2.3
faker==34.0.0
python-dotenv==1.0.1
uvicorn[standard]==0.34.0
pydantic==2.10.6
psycopg2-binary==2.9.10
```

### 4. `.env.example`
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Pinecone Configuration
PINECONE_API_KEY=YOUR_KEY_HERE
PINECONE_INDEX_NAME=matchmaking-players
PINECONE_ENVIRONMENT=us-east-1

# Database (no cambiar, usa docker-compose)
DATABASE_URL=postgresql://pader:pader123@postgres:5432/matchmaking
```

### 5. `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
*.log

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
```

### 6. `init.sql`
```sql
-- Crear tabla de jugadores
CREATE TABLE IF NOT EXISTS players (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    elo INTEGER NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    positions JSONB NOT NULL,
    location JSONB NOT NULL,
    availability JSONB,
    acceptance_rate FLOAT NOT NULL DEFAULT 0.5,
    last_active_days INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar performance
CREATE INDEX idx_players_elo ON players(elo);
CREATE INDEX idx_players_category ON players(category);
CREATE INDEX idx_players_gender ON players(gender);
CREATE INDEX idx_players_acceptance_rate ON players(acceptance_rate DESC);
CREATE INDEX idx_players_last_active ON players(last_active_days);

-- Insertar un jugador de prueba
INSERT INTO players (id, name, elo, age, gender, category, positions, location, availability, acceptance_rate, last_active_days)
VALUES (
    'test-player-001',
    'Juan Test',
    1500,
    28,
    'MALE',
    'SEVENTH',
    '["FOREHAND", "BACKHAND"]'::jsonb,
    '{"lat": -31.42647, "lon": -64.18722, "zone": "Nueva Córdoba"}'::jsonb,
    '[{"min": "18:00", "max": "22:00"}]'::jsonb,
    0.85,
    2
);
```

### 7. `src/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
```

### 8. `src/config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "matchmaking-players")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Validación
    @classmethod
    def validate(cls):
        required = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
            ("DATABASE_URL", cls.DATABASE_URL),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

config = Config()
```

### 9. `README.md` (del repo)
```markdown
# 🚀 PADER Matchmaking AI

Microservicio de matchmaking con IA para encontrar jugadores compatibles en PADER.

## 🏃 Quick Start

### 1. Clonar y configurar
\`\`\`bash
git clone <repo-url>
cd matchmaking-ai

# Copiar template de variables
cp .env.example .env

# Editar .env con tus API keys
nano .env
\`\`\`

### 2. Levantar servicios
\`\`\`bash
docker-compose up --build
\`\`\`

### 3. Verificar
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🧪 Tests Rápidos

### Test PostgreSQL
\`\`\`bash
docker exec -it matchmaking_db psql -U pader -d matchmaking -c "SELECT * FROM players;"
\`\`\`

### Test API
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

## 📚 Documentación

Ver carpeta `/docs` para documentación completa de la hackathon.

## 🛠️ Comandos Útiles

\`\`\`bash
# Ver logs
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Rebuild completo
docker-compose down -v
docker-compose up --build

# Acceder a la DB
docker exec -it matchmaking_db psql -U pader -d matchmaking
\`\`\`
\`\`\`

### 10. Crear todos los `__init__.py`
```python
# Archivo vacío para que Python reconozca como paquete
```

---

## 🚀 Pasos para Preparar el Repo

### 1. Crear estructura
```bash
mkdir -p matchmaking-ai/{src/{models,services,external,database,routers,seeders,utils},tests}
cd matchmaking-ai
```

### 2. Crear archivos base
```bash
# Crear todos los __init__.py
touch src/__init__.py
touch src/{models,services,external,database,routers,seeders,utils}/__init__.py
touch tests/__init__.py

# Crear archivos de configuración
touch Dockerfile docker-compose.yml requirements.txt
touch .env.example .gitignore init.sql
touch src/main.py src/config.py
touch README.md
```

### 3. Copiar contenido
Copiar el contenido de cada archivo según lo especificado arriba.

### 4. Configurar APIs

#### OpenAI:
1. Ir a https://platform.openai.com/api-keys
2. Crear nueva key
3. Copiar y pegar en `.env`

#### Pinecone:
1. Ir a https://app.pinecone.io/
2. Crear cuenta y proyecto
3. Crear índice:
   - Name: `matchmaking-players`
   - Dimensions: `1536`
   - Metric: `cosine`
   - Cloud: `AWS`
   - Region: `us-east-1`
4. Copiar API key y pegar en `.env`

### 5. Test inicial
```bash
# Levantar servicios
docker-compose up --build

# En otra terminal, verificar
curl http://localhost:8000/health

# Verificar DB
docker exec -it matchmaking_db psql -U pader -d matchmaking -c "SELECT COUNT(*) FROM players;"
# Debería retornar 1 (el jugador de prueba)
```

---

## ✅ Checklist Pre-Hackathon

- [ ] Repo creado en GitHub
- [ ] Estructura de carpetas completa
- [ ] Todos los archivos base creados
- [ ] `.env` configurado con API keys reales
- [ ] Docker Desktop instalado y corriendo
- [ ] `docker-compose up` funciona sin errores
- [ ] Endpoint `/health` responde OK
- [ ] PostgreSQL tiene tabla `players` con 1 registro
- [ ] OpenAI API key válida (test de embedding)
- [ ] Pinecone índice creado y accesible
- [ ] README.md con instrucciones claras
- [ ] Documentación de hackathon en `/docs`

---

## 🎯 Día de la Hackathon

Los devs solo necesitan:

```bash
# 1. Clonar
git clone <repo-url>
cd matchmaking-ai

# 2. Configurar (si no está en el repo)
cp .env.example .env
# Editar .env con las keys compartidas

# 3. Levantar
docker-compose up

# 4. Empezar a codear!
```

Todo el setup toma **menos de 5 minutos**. 🚀

---

## 💡 Tips Adicionales

### Hot Reload
El volumen `./src:/app/src` en docker-compose permite hot reload. Los cambios en el código se reflejan automáticamente.

### Debugging
Para debugging, puedes agregar breakpoints y usar:
```bash
docker-compose run --service-ports api python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Variables de Entorno Compartidas
Para la hackathon, puedes compartir un `.env` con las API keys del equipo (en un canal privado de Slack, NO en el repo público).

### Backup de Datos
Si quieres preservar datos entre reinicios:
```bash
# Backup
docker exec matchmaking_db pg_dump -U pader matchmaking > backup.sql

# Restore
docker exec -i matchmaking_db psql -U pader matchmaking < backup.sql
```

---

**Con este setup, el día de la hackathon es 100% desarrollo, 0% configuración.** ⚡
