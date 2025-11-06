# ⚡ QUICK START - Setup en 30 minutos

## 📋 Pre-requisitos

- [ ] Python 3.11+
- [ ] Docker Desktop
- [ ] Git
- [ ] Cuenta OpenAI (con créditos)
- [ ] Cuenta Pinecone (free tier)
- [ ] Postman o Insomnia

---

## 🚀 Setup Paso a Paso

### 1. Crear repositorio (5 min)

```bash
# Crear carpeta del proyecto
mkdir matchmaking-ai
cd matchmaking-ai

# Inicializar git
git init
git remote add origin <tu-repo-url>

# Crear estructura de carpetas
mkdir -p src/{models,services,external,database,routers,seeders,utils}
touch src/__init__.py
touch src/main.py
```

### 2. Configurar entorno Python (5 min)

```bash
# Crear virtual environment
python -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate

# Crear requirements.txt
cat > requirements.txt << EOF
fastapi[standard]==0.115.0
openai==1.54.0
pinecone-client==5.0.0
numpy==2.1.0
pandas==2.2.0
faker==30.8.0
python-dotenv==1.0.1
uvicorn[standard]==0.32.0
pydantic==2.9.0
psycopg2-binary==2.9.9
EOF

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar OpenAI (5 min)

```bash
# Ir a https://platform.openai.com/api-keys
# Crear nueva API key
# Copiar la key (empieza con sk-proj-...)

# Crear archivo .env
cat > .env << EOF
OPENAI_API_KEY=sk-proj-TU_KEY_AQUI
PINECONE_API_KEY=pendiente
PINECONE_INDEX_NAME=matchmaking-players
PINECONE_ENVIRONMENT=us-east-1
DATABASE_URL=postgresql://pader:pader123@localhost:5432/pader_mock
EOF
```

### 4. Configurar Pinecone (5 min)

```bash
# Ir a https://app.pinecone.io/
# Crear cuenta gratuita
# Crear nuevo proyecto
# Crear índice:
#   - Name: matchmaking-players
#   - Dimensions: 1536
#   - Metric: cosine
#   - Cloud: AWS
#   - Region: us-east-1

# Copiar API key desde Settings
# Actualizar .env con la key
```

### 5. Levantar PostgreSQL (5 min)

```bash
# Crear docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: pader_mock_db
    environment:
      POSTGRES_USER: pader
      POSTGRES_PASSWORD: pader123
      POSTGRES_DB: pader_mock
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# Levantar container
docker-compose up -d

# Verificar que está corriendo
docker ps
```

### 6. Crear tabla de jugadores (5 min)

```bash
# Conectarse a la DB
docker exec -it pader_mock_db psql -U pader -d pader_mock

# Ejecutar SQL
CREATE TABLE players (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    elo INTEGER,
    age INTEGER,
    gender VARCHAR(10),
    category VARCHAR(20),
    positions JSONB,
    location JSONB,
    availability JSONB,
    acceptance_rate FLOAT,
    last_active_days INTEGER
);

# Salir
\q
```

---

## 🧪 Verificar Setup

### Test 1: OpenAI funciona
```bash
python << EOF
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Test embedding"
)

print(f"✅ OpenAI OK - Embedding dimension: {len(response.data[0].embedding)}")
EOF
```

### Test 2: Pinecone funciona
```bash
python << EOF
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index("matchmaking-players")
stats = index.describe_index_stats()

print(f"✅ Pinecone OK - Vectors: {stats['total_vector_count']}")
EOF
```

### Test 3: PostgreSQL funciona
```bash
python << EOF
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM players")
count = cursor.fetchone()[0]

print(f"✅ PostgreSQL OK - Players: {count}")
EOF
```

---

## 🏃 Correr la aplicación

### Opción 1: Desarrollo
```bash
# Desde la raíz del proyecto
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Producción
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verificar que está corriendo
```bash
curl http://localhost:8000/
# Debería retornar: {"message": "PADER Matchmaking AI - Hackathon 2025"}

curl http://localhost:8000/api/matchmaking/health
# Debería retornar: {"status": "healthy", ...}
```

---

## 📝 Primeros pasos

### 1. Seed jugadores mock
```bash
curl -X POST http://localhost:8000/api/matchmaking/seed_players/100
```

### 2. Buscar candidatos
```bash
curl -X POST http://localhost:8000/api/matchmaking/find_candidates \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "test-001",
    "categories": ["SEVENTH", "SIXTH"],
    "elo_range": [1400, 1800],
    "gender_preference": "MALE",
    "required_players": 3,
    "location": {"lat": -31.42647, "lon": -64.18722, "zone": "Nueva Córdoba"},
    "match_time": "19:00",
    "required_time": 90
  }'
```

---

## 🐛 Troubleshooting

### Error: "OpenAI API key not found"
```bash
# Verificar que .env existe y tiene la key
cat .env | grep OPENAI_API_KEY

# Verificar que python-dotenv está instalado
pip list | grep python-dotenv

# Verificar que se está cargando el .env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Error: "Pinecone index not found"
```bash
# Verificar que el índice existe
python << EOF
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
print(pc.list_indexes())
EOF

# Si no existe, crearlo desde el dashboard de Pinecone
```

### Error: "Connection refused" (PostgreSQL)
```bash
# Verificar que el container está corriendo
docker ps | grep pader_mock_db

# Si no está, levantarlo
docker-compose up -d

# Verificar logs
docker logs pader_mock_db
```

### Error: "Module not found"
```bash
# Verificar que el venv está activado
which python
# Debería mostrar: /path/to/matchmaking-ai/venv/bin/python

# Si no, activar
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

---

## 📚 Recursos útiles

### Documentación
- FastAPI: https://fastapi.tiangolo.com/
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- Pinecone: https://docs.pinecone.io/
- Pydantic: https://docs.pydantic.dev/

### Herramientas
- Postman: https://www.postman.com/downloads/
- Insomnia: https://insomnia.rest/download
- DBeaver (DB client): https://dbeaver.io/download/

### Monitoreo
- FastAPI Docs: http://localhost:8000/docs (Swagger UI automático)
- Pinecone Dashboard: https://app.pinecone.io/
- Docker Desktop: Para ver logs de PostgreSQL

---

## ✅ Checklist de Setup Completo

- [ ] Python 3.11+ instalado
- [ ] Virtual environment creado y activado
- [ ] Dependencias instaladas (requirements.txt)
- [ ] Cuenta OpenAI creada y API key configurada
- [ ] Cuenta Pinecone creada e índice creado
- [ ] PostgreSQL corriendo en Docker
- [ ] Tabla `players` creada
- [ ] Tests de conexión pasando (OpenAI, Pinecone, PostgreSQL)
- [ ] Aplicación corriendo en http://localhost:8000
- [ ] Endpoint /health retornando OK
- [ ] 100 jugadores seeded exitosamente
- [ ] Primer request de matchmaking funcionando

---

## 🎯 Siguiente paso

Una vez completado este setup, estás listo para empezar a desarrollar siguiendo el **PLAN.md**.

Cada team puede trabajar en paralelo en sus archivos asignados. La integración será más fácil si todos siguen las interfaces definidas en **TECHNICAL-SPECS.md**.

**¡Manos a la obra! 🚀**
