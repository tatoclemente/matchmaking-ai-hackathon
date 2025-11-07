# 🚀 PADER Matchmaking AI

Microservicio de matchmaking con IA para encontrar jugadores compatibles en PADER.

## 🏃 Quick Start

### 1. Clonar y configurar
```bash
git clone <repo-url>
cd matchmaking-ai

# Copiar template de variables
cp .env.example .env

# Editar .env con tus API keys
nano .env
```

### 2. Levantar servicios
```bash
docker-compose up --build
```

### 3. Verificar
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🧪 Tests

### Ejecutar todos los tests
```bash
./run_tests.sh
```

Esto ejecuta:
- ✓ Test de cálculo de distancias (Haversine)
- ✓ Test de scoring service completo
- ✓ Test de mensajes personalizados

### Tests individuales

**Test Scoring Service:**
```bash
export PYTHONPATH=.
python3 tests/test_scoring_service.py
```

**Test Haversine Distance:**
```bash
export PYTHONPATH=.
python3 -c "from tests.utils.test_geo_utils import test_haversine_distance; test_haversine_distance(); print('✓ Test passed')"
```

### Tests de integración

**Test PostgreSQL:**
```bash
docker exec -it matchmaking_db psql -U pader -d matchmaking -c "SELECT * FROM players;"
```

**Test API:**
```bash
curl http://localhost:8000/health
```

## 📚 Documentación

Ver carpeta `/hackathon` para documentación completa de la hackathon.

## 🛠️ Comandos Útiles

```bash
# Ver logs
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Rebuild completo
docker-compose down -v
docker-compose up --build

# Acceder a la DB
docker exec -it matchmaking_db psql -U pader -d matchmaking
```
