# 🎯 CONTEXTO DEL PRODUCTO - Microservicio de Matchmaking IA

## ¿Qué es PADER?

PADER es una plataforma de gestión de partidos de pádel que conecta jugadores, gestiona matches y mantiene un sistema de ranking ELO. El sistema actual permite a los usuarios crear partidos y buscar jugadores manualmente.

## El Problema

Actualmente, cuando un jugador crea un partido y necesita completar el cupo (4 jugadores en total para dobles), debe:
1. Buscar manualmente en listas de jugadores
2. Enviar invitaciones sin saber quién es más compatible
3. Esperar respuestas que pueden no llegar
4. Repetir el proceso si alguien rechaza

**Resultado:** Baja tasa de matches completados, frustración de usuarios, partidos desbalanceados.

## La Solución: Matchmaking con IA

Un microservicio inteligente que:
- **Analiza** el perfil del partido y los jugadores disponibles
- **Predice** qué jugadores son más compatibles usando embeddings
- **Prioriza** jugadores confiables con alta tasa de aceptación
- **Recomienda** candidatos ranqueados por probabilidad de match exitoso

## Flujo de Usuario (Automático)

### Escenario actual (sin IA):
```
Usuario crea partido → Ve lista de 500 jugadores → Invita a 10 al azar → 2 aceptan → Repite
```

### Escenario con IA (Automático):
```
Usuario crea partido → "Buscando jugadores..." → IA encuentra top 20 → PADER envía invitaciones automáticamente → Jugadores reciben "Partido compatible encontrado" → 15+ aceptan → Match completo en minutos
```

### Experiencia del jugador invitado:
```
Notificación: "🎾 Partido compatible en Nueva Córdoba - 19:00hs (95% match)" → Ve detalles → Botón "Unirse" → Confirmado
```

## Valor del Negocio

### Métricas de impacto:
- **↑ Tasa de matches completados:** De 40% a 85%
- **↓ Tiempo para completar partido:** De 2 horas a 15 minutos
- **↑ Satisfacción de usuarios:** Partidos más balanceados y divertidos
- **↑ Retención:** Usuarios vuelven porque encuentran matches fácilmente

### ROI para PADER:
- Más partidos completados = más engagement
- Usuarios satisfechos = menor churn
- Matches balanceados = mejor experiencia = más referidos

## Casos de Uso Principales

### 1. Completar partido casual
**Usuario:** Martín, categoría SEXTA, quiere jugar hoy a las 19:00
**Necesidad:** 3 jugadores de nivel similar, cerca de su zona
**IA sugiere:** Jugadores con ELO 1700-1900, disponibles 19:00-21:00, a <3km

### 2. Encontrar jugador de posición específica
**Usuario:** Club organizando torneo, falta un jugador de revés
**Necesidad:** Jugador de BACKHAND, categoría QUINTA o superior
**IA sugiere:** Jugadores que prefieren revés, con alta acceptance_rate

### 3. Match de último momento
**Usuario:** Se canceló un jugador 30 min antes del partido
**Necesidad:** Reemplazo urgente, mismo nivel, cerca
**IA sugiere:** Jugadores muy activos (last_active < 1 día), zona cercana

## Diferenciadores de la IA

### 1. Embeddings semánticos
No solo matchea por ELO, captura "estilo de juego":
- Jugadores agresivos con jugadores defensivos
- Preferencias de horario y zona
- Patrones de comportamiento

### 2. Scoring multi-dimensional
Considera 6 factores simultáneamente:
- Compatibilidad técnica (ELO, categoría)
- Logística (distancia, horario)
- Confiabilidad (acceptance_rate, actividad)

### 3. Aprendizaje continuo (roadmap)
El sistema mejora con cada match:
- Aprende qué combinaciones funcionan
- Ajusta pesos según feedback
- Predice probabilidad de aceptación

## Arquitectura de Integración (Futuro)

```
┌─────────────────┐
│  PADER Server   │
│  (Node.js)      │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Matchmaking IA │
│  (FastAPI)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Pinecone│ │PostgreSQL│
│(Vector)│ │  (Data)  │
└────────┘ └──────────┘
```

### Flujo de datos (Automático):
1. **PADER** crea partido → envía request a **Matchmaking IA**
2. **Matchmaking IA** consulta embeddings en **Pinecone**
3. **Matchmaking IA** enriquece con datos de **PostgreSQL**
4. **Matchmaking IA** retorna top 20 candidatos ranqueados a **PADER**
5. **PADER** envía invitaciones automáticamente (push notifications/email)
6. Jugadores reciben "Partido compatible encontrado" con detalles
7. Jugadores aceptan/rechazan → **PADER** actualiza métricas en **PostgreSQL**

## Datos Clave del Sistema

### Jugador (Player)
```
- Perfil técnico: ELO, categoría, posiciones
- Perfil personal: edad, género, ubicación
- Comportamiento: acceptance_rate, last_active_days
- Disponibilidad: rangos horarios
```

### Partido (Match Request)
```
- Requisitos técnicos: categorías, rango ELO
- Requisitos logísticos: ubicación, horario, duración
- Preferencias: género, edad, posición específica
```

### Candidato (Candidate)
```
- Score total (0.0-1.0)
- Breakdown de scoring
- Razones de compatibilidad
- Métricas de distancia y ELO
```

## Métricas de Éxito del Microservicio

### Performance:
- ✅ Latencia < 200ms para encontrar candidatos
- ✅ Soportar 1000+ jugadores indexados
- ✅ 99.9% uptime

### Calidad:
- ✅ Top 3 candidatos tienen >80% acceptance rate
- ✅ Matches sugeridos tienen ELO diff < 150
- ✅ 90% de usuarios satisfechos con sugerencias

### Escalabilidad:
- ✅ Arquitectura lista para millones de jugadores
- ✅ Indexación en tiempo real
- ✅ Búsqueda vectorial optimizada

## Roadmap de Producto

### Hackathon (Día 1):
- ✅ MVP funcional con IA real
- ✅ 1000 jugadores mock
- ✅ Demo impresionante

### Fase 1 (Semana 1-2):
- Integración con PADER server
- Sincronización de datos
- Testing con usuarios reales

### Fase 2 (Mes 1):
- Webhooks para actualización en tiempo real
- Dashboard de métricas
- A/B testing de algoritmos

### Fase 3 (Mes 2-3):
- Aprendizaje continuo
- Recomendaciones proactivas
- Sistema de reputación

## Consideraciones Técnicas

### Por qué FastAPI:
- Rápido y moderno
- Async nativo
- Documentación automática
- Fácil integración con Python ML libs

### Por qué Pinecone:
- Vector search optimizado
- Escalabilidad automática
- Filtros metadata
- Latencia ultra-baja

### Por qué OpenAI Embeddings:
- Calidad superior
- 1536 dimensiones
- Captura semántica compleja
- API simple y confiable

## Glosario de Términos

- **ELO:** Sistema de ranking numérico (800-3300+)
- **Categoría:** Clasificación por nivel (NINTH a FIRST)
- **Embedding:** Vector de 1536 números que representa un jugador
- **Acceptance rate:** Porcentaje de invitaciones aceptadas (0.0-1.0)
- **Vector similarity:** Similitud coseno entre embeddings (0.0-1.0)
- **Scoring:** Algoritmo que combina múltiples factores en un score final

---

**Este microservicio es el cerebro del matchmaking de PADER. Convierte un problema de búsqueda manual en una experiencia mágica donde la IA encuentra el match perfecto en segundos.**
