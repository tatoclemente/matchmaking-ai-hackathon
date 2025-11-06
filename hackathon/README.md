# 🚀 HACKATHON - Microservicio Matchmaking IA

Este directorio contiene toda la documentación necesaria para construir el microservicio de matchmaking con IA para PADER en el contexto de una hackathon de 1 día.

---

## 📁 Documentos Disponibles

### 1. **PLAN.md** - Plan de Ejecución Principal
**Propósito:** Guía paso a paso para la hackathon con división de trabajo por equipos.

**Contenido:**
- Arquitectura del microservicio
- División de trabajo (4 teams, 8 devs)
- Tareas específicas por equipo
- Código de ejemplo para cada componente
- Timeline de 8 horas
- Checklist de éxito
- Escenario de demo final

**Cuándo usar:** Este es tu documento principal. Léelo primero y úsalo como roadmap durante toda la hackathon.

---

### 2. **PRODUCT-CONTEXT.md** - Contexto del Producto
**Propósito:** Entender el problema de negocio y el valor del microservicio.

**Contenido:**
- ¿Qué es PADER y qué problema resuelve?
- Casos de uso principales
- Flujo de usuario antes/después de la IA
- Métricas de impacto y ROI
- Arquitectura de integración futura
- Roadmap del producto

**Cuándo usar:** Para entender el "por qué" detrás del microservicio. Útil para la presentación final y para tomar decisiones de diseño.

---

### 3. **TECHNICAL-SPECS.md** - Especificaciones Técnicas
**Propósito:** Referencia técnica detallada de la implementación.

**Contenido:**
- Arquitectura en capas
- Modelos de datos completos (Pydantic)
- Algoritmo de embeddings explicado
- Algoritmo de scoring detallado (con fórmulas)
- Flujo de datos completo
- Configuración de Pinecone
- Manejo de errores
- Testing strategy
- Performance optimization

**Cuándo usar:** Durante el desarrollo cuando necesites detalles técnicos específicos. Es tu "manual de referencia".

---

### 4. **QUICK-START.md** - Setup Rápido
**Propósito:** Poner el entorno de desarrollo funcionando en 30 minutos.

**Contenido:**
- Pre-requisitos
- Setup paso a paso (Python, OpenAI, Pinecone, PostgreSQL)
- Tests de verificación
- Comandos para correr la app
- Troubleshooting común
- Checklist de setup completo

**Cuándo usar:** Al inicio de la hackathon para configurar el entorno. También útil para debugging de problemas de setup.

---

### 5. **SETUP-BASE.md** - Preparación del Repositorio Base
**Propósito:** Crear el repositorio con todo configurado ANTES de la hackathon.

**Contenido:**
- Estructura completa de archivos
- Dockerfile y docker-compose.yml
- Configuración de PostgreSQL con init.sql
- FastAPI base con hot reload
- Scripts de verificación
- Checklist pre-hackathon

**Cuándo usar:** ANTES de la hackathon para preparar el repo. El día del evento solo será `docker-compose up` y empezar a codear.

---

### 6. **AI-AGENT-INSTRUCTIONS.md** - Guía para Agentes de IA
**Propósito:** Instrucciones específicas para agentes de IA que ayudarán a construir el microservicio.

**Contenido:**
- Tareas por componente con referencias exactas
- Reglas críticas de implementación
- Orden de lectura de documentos
- Checklist de verificación por componente
- Datos de ejemplo y mocks
- Orden de implementación recomendado

**Cuándo usar:** Como contexto principal para agentes de IA (Claude, GPT, etc.) que implementarán el código. Proporciona instrucciones claras y referencias a las especificaciones.

---

### 7. **EVOLUTION-ROADMAP.md** - Plan de Evolución con IA
**Propósito:** Roadmap completo desde prototipo hasta sistema de IA que aprende continuamente.

**Contenido:**
- 5 fases de evolución (Hackathon → IA Avanzada)
- Sistema de feedback y aprendizaje continuo
- A/B testing y optimización automática
- Fine-tuning de embeddings con datos reales
- Pipeline de aprendizaje supervisado
- Métricas de evolución y KPIs
- Script para demo final con roadmap

**Cuándo usar:** Para la presentación final, explicar el futuro del sistema y cómo evolucionará con aprendizaje continuo. Esencial para mostrar visión a largo plazo.

---

## 🎯 Flujo de Trabajo Recomendado

### Antes de la Hackathon (1-2 días antes)
1. ✅ **[ORGANIZADOR]** Seguir **SETUP-BASE.md** para crear repo base
2. ✅ **[ORGANIZADOR]** Configurar API keys y verificar servicios
3. ✅ **[TODOS]** Leer **PRODUCT-CONTEXT.md** para entender el problema
4. ✅ **[TODOS]** Leer **PLAN.md** completo
5. ✅ **[TODOS]** Clonar repo y verificar `docker-compose up`
6. ✅ **[ORGANIZADOR]** Asignar teams y responsabilidades

### Durante la Hackathon (Día 1)

#### Hora 0-1: Setup y Planificación
- Todos siguen **QUICK-START.md**
- Revisar **PLAN.md** sección "División de Trabajo"
- Crear repo Git y estructura de carpetas

#### Hora 1-4: Desarrollo Paralelo
- **Team 1:** Implementar modelos (referencia: **TECHNICAL-SPECS.md** → Modelos de Datos)
- **Team 2:** Implementar servicios externos (referencia: **TECHNICAL-SPECS.md** → External Layer)
- **Team 3:** Implementar matchmaking y scoring (referencia: **TECHNICAL-SPECS.md** → Algoritmo de Scoring)
- **Team 4:** Implementar API y seeders (referencia: **PLAN.md** → Team 4)

#### Hora 4-5: Almuerzo e Integración
- Merge de branches
- Resolver conflictos
- Primera prueba end-to-end

#### Hora 5-7: Testing y Refinamiento
- Seed 1000 jugadores
- Testing de endpoints
- Ajustar scoring si es necesario
- Preparar datos para demo

#### Hora 7-8: Demo y Presentación
- Seguir escenario de **PLAN.md** → Demo Final
- Usar contexto de **PRODUCT-CONTEXT.md** para la presentación
- Mostrar métricas y resultados

---

## 📊 Estructura del Microservicio

```
matchmaking-ai/
├── src/
│   ├── models/              # Pydantic models (Team 1)
│   │   ├── player.py
│   │   ├── match_request.py
│   │   └── candidate.py
│   │
│   ├── services/            # Business logic (Team 3)
│   │   ├── matchmaking_service.py
│   │   └── scoring_service.py
│   │
│   ├── external/            # External clients (Team 2)
│   │   ├── openai_client.py
│   │   ├── pinecone_client.py
│   │   └── config.py
│   │
│   ├── database/            # DB client (Team 2)
│   │   └── db_client.py
│   │
│   ├── routers/             # FastAPI endpoints (Team 4)
│   │   └── matchmaking.py
│   │
│   ├── seeders/             # Mock data (Team 4)
│   │   ├── player_seeder.py
│   │   └── db_seeder.py
│   │
│   ├── utils/               # Utilities (Team 3)
│   │   ├── geo_utils.py
│   │   └── time_utils.py
│   │
│   └── main.py              # FastAPI app (Team 4)
│
├── docker-compose.yml       # PostgreSQL
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
└── README.md
```

---

## 🔑 Conceptos Clave

### Embeddings
Vectores de 1536 números que representan el "significado" de un jugador o partido. Jugadores similares tienen embeddings similares.

### Vector Search
Búsqueda en Pinecone que encuentra jugadores con embeddings similares al embedding del partido.

### Scoring Multi-dimensional
Algoritmo que combina 6 factores (similitud vectorial, ELO, distancia, horario, acceptance rate, actividad) en un score final de 0.0 a 1.0.

### Acceptance Rate
Métrica de confiabilidad: porcentaje de invitaciones que un jugador acepta. Jugadores con alta acceptance rate son priorizados.

---

## 🎓 Para Presentar a los Jueces

### Elevator Pitch (30 segundos)
"Creamos un motor de matchmaking con IA que encuentra automáticamente los 20 mejores jugadores para tu partido de pádel. Cuando creas un partido, PADER envía invitaciones personalizadas instantáneamente. Los jugadores reciben 'Partido muy compatible en tu zona - 95% match' y solo tocan 'Unirse'. Sin búsqueda manual, sin fricción. Resultado: 90% de matches completados vs 40% actual."

### Demo Script (5 minutos)
1. **Problema:** "Encontrar jugadores es frustrante - 60% de partidos no se completan"
2. **Solución:** "IA que envía invitaciones automáticamente a jugadores perfectos"
3. **Demo en vivo:** Crear partido → Top 20 candidatos en <200ms → "Enviando invitaciones..."
4. **Experiencia del jugador:** Mostrar notificación "Partido compatible - 95% match"
5. **Magia de la IA:** Embeddings + scoring + mensajes personalizados
6. **Roadmap:** Sistema aprende continuamente, 95% precisión en 12 meses

### Preguntas Frecuentes

**P: ¿Por qué usar embeddings en vez de solo filtros?**
R: Los embeddings capturan similitud semántica que los filtros no pueden. Por ejemplo, dos jugadores con mismo ELO pero estilos opuestos (agresivo vs defensivo) pueden no ser compatibles. Los embeddings aprenden estos patrones.

**P: ¿Cómo escala con millones de jugadores?**
R: Pinecone está diseñado para búsqueda vectorial a escala. Soporta millones de vectores con latencia <100ms. Además, usamos filtros metadata para reducir el espacio de búsqueda.

**P: ¿Qué pasa si un jugador no especifica disponibilidad?**
R: Asumimos disponibilidad media (score 0.5) para no penalizarlo demasiado. En producción, podríamos inferir disponibilidad de su historial.

**P: ¿Cómo se integra con PADER?**
R: PADER hace requests HTTP al microservicio. En el futuro, webhooks para sincronización en tiempo real de métricas como acceptance_rate. Ver **EVOLUTION-ROADMAP.md** para plan completo de integración y evolución.

**P: ¿Cómo mejora el sistema con el tiempo?**
R: Sistema de aprendizaje continuo que optimiza pesos, reentrena embeddings y predice compatibilidad basado en feedback real. Evolución de 60% a 95% de precisión en 12 meses.

---

## 🤖 Para Agentes de IA

Si eres un agente de IA construyendo este microservicio:
1. **PRIMERO:** Lee **AI-AGENT-INSTRUCTIONS.md** completo
2. **SEGUNDO:** Consulta **TECHNICAL-SPECS.md** para detalles técnicos
3. **TERCERO:** Usa **PLAN.md** para código de ejemplo
4. **Siempre:** Sigue las especificaciones exactas, no improvises

---

## 📞 Contacto y Soporte

Durante la hackathon, si tienes dudas:
1. Revisa el documento correspondiente (PLAN, TECHNICAL-SPECS, etc.)
2. Busca en la sección de Troubleshooting de **QUICK-START.md**
3. Consulta con tu team lead
4. Pregunta en el canal de Slack del evento

---

## ✅ Checklist Final

Antes de presentar, verifica:
- [ ] Todos los endpoints funcionan
- [ ] 1000+ jugadores indexados
- [ ] Demo preparada con datos realistas
- [ ] Métricas de performance medidas
- [ ] Presentación lista (slides o script)
- [ ] Código en GitHub con README
- [ ] Video de demo (backup por si falla internet)

---

## 🏆 Criterios de Éxito

### Técnico
- ✅ IA funcional con embeddings reales
- ✅ Scoring multi-dimensional implementado
- ✅ Latencia <200ms
- ✅ Datos realistas y creíbles

### Presentación
- ✅ Demo impresionante y fluida
- ✅ Explicación clara del valor de negocio
- ✅ Arquitectura escalable y profesional
- ✅ Roadmap convincente

### Impacto
- ✅ Resuelve un problema real
- ✅ Métricas de impacto claras
- ✅ Diferenciación vs competencia
- ✅ Viabilidad de implementación

---

**¡Éxito en la hackathon! 🚀**

Este microservicio tiene el potencial de transformar la experiencia de matchmaking en PADER. Construyámoslo juntos.
