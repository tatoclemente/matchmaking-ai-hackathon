/**
 * 🏗️ GUÍA DE INFRAESTRUCTURA - MATCHMAKING AI
 * Implementación TypeScript de los Servicios Externos
 * 
 * Esta guía contiene código TypeScript listo para usar para:
 * - OpenAI Embeddings Service
 * - Pinecone Vector Store
 * - PostgreSQL Database Client
 * - Configuración y Dependency Injection
 */

// ============================================================================
// 📦 TYPES & INTERFACES
// ============================================================================

/**
 * Player Model - Representa un jugador de pádel
 */
interface Player {
    id: string;
    name: string;
    elo: number; // 800-3300+
    age: number; // 18-60
    gender: "MALE" | "FEMALE";
    category: Category;
    positions: Position[];
    location: Location;
    availability?: TimeSlot[];
    acceptance_rate: number; // 0.0-1.0
    last_active_days: number;
}

/**
 * Match Request - Requisitos del partido
 */
interface MatchRequest {
    match_id: string;
    categories: Category[];
    elo_range: [number, number];
    age_range?: [number, number];
    gender_preference: "MALE" | "FEMALE" | "MIXED";
    required_players: number; // 1-3
    location: Location;
    match_time: string; // "HH:MM"
    required_time: number; // minutos
    preferred_position?: Position;
}

/**
 * Candidate - Resultado del matchmaking
 */
interface Candidate {
    player_id: string;
    player_name: string;
    score: number; // 0.0-1.0
    distance_km: number;
    elo: number;
    elo_diff: number;
    acceptance_rate: number;
    reasons: string[];
    invitation_message: string;
    compatibility_summary: string;
}

/**
 * Enums y tipos auxiliares
 */
type Category = 
    | "NINTH" 
    | "EIGHTH" 
    | "SEVENTH" 
    | "SIXTH" 
    | "FIFTH" 
    | "FOURTH" 
    | "THIRD" 
    | "SECOND" 
    | "FIRST";

type Position = "FOREHAND" | "BACKHAND";

interface Location {
    lat: number;
    lon: number;
    zone: string;
}

interface TimeSlot {
    min: string; // "HH:MM"
    max: string; // "HH:MM"
}

/**
 * Configuración del sistema
 */
interface AppConfig {
    openai_api_key: string;
    pinecone_api_key: string;
    pinecone_index_name: string;
    pinecone_environment: string;
    database_url: string;
    log_level: string;
    max_candidates: number;
}

// ============================================================================
// 🤖 OPENAI EMBEDDINGS SERVICE
// ============================================================================

/**
 * EmbeddingService - Genera embeddings usando OpenAI API
 * 
 * Responsabilidades:
 * - Crear embeddings de jugadores (1536 dimensiones)
 * - Crear embeddings de match requests
 * - Construir textos descriptivos ricos
 */
class EmbeddingService {
    private apiKey: string;
    private model: string = "text-embedding-3-small";
    private baseUrl: string = "https://api.openai.com/v1/embeddings";

    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }

    /**
     * Crear embedding del perfil de un jugador
     * @param player - Objeto Player
     * @returns Vector de 1536 dimensiones
     */
    async createPlayerEmbedding(player: Player): Promise<number[]> {
        const description = this.buildPlayerDescription(player);
        
        try {
            const embedding = await this.createEmbedding(description);
            
            // Validar dimensiones
            if (embedding.length !== 1536) {
                throw new Error(`Invalid embedding dimensions: ${embedding.length}`);
            }
            
            return embedding;
        } catch (error) {
            throw new EmbeddingError(`Error creating player embedding: ${error.message}`);
        }
    }

    /**
     * Crear embedding de los requisitos del partido
     * @param request - Objeto MatchRequest
     * @returns Vector de 1536 dimensiones
     */
    async createRequestEmbedding(request: MatchRequest): Promise<number[]> {
        const description = this.buildRequestDescription(request);
        
        try {
            const embedding = await this.createEmbedding(description);
            return embedding;
        } catch (error) {
            throw new EmbeddingError(`Error creating request embedding: ${error.message}`);
        }
    }

    /**
     * Construir descripción rica del jugador para el embedding
     * @private
     */
    private buildPlayerDescription(player: Player): string {
        const parts: string[] = [
            `Jugador de pádel categoría ${player.category}`,
            `ELO ${player.elo}`,
            `Edad ${player.age} años`,
            `Género ${player.gender}`,
            `Juega de ${player.positions.join(' y ')}`,
            `Zona ${player.location.zone}`
        ];

        // Agregar disponibilidad si existe
        if (player.availability && player.availability.length > 0) {
            const timeRanges = player.availability
                .map(slot => `${slot.min}-${slot.max}`)
                .join(', ');
            parts.push(`Disponible ${timeRanges}`);
        }

        // Agregar contexto comportamental
        if (player.acceptance_rate > 0.8) {
            parts.push("Jugador muy confiable y activo");
        } else if (player.acceptance_rate < 0.4) {
            parts.push("Jugador ocasional");
        }

        if (player.last_active_days < 3) {
            parts.push("Usuario muy activo recientemente");
        }

        return parts.join(". ") + ".";
    }

    /**
     * Construir descripción de los requisitos del partido
     * @private
     */
    private buildRequestDescription(request: MatchRequest): string {
        const parts: string[] = [
            `Partido de pádel categorías ${request.categories.join(', ')}`,
            `ELO entre ${request.elo_range[0]} y ${request.elo_range[1]}`,
            `Zona ${request.location.zone}`,
            `Horario ${request.match_time}`,
            `Duración ${request.required_time} minutos`,
            `Género ${request.gender_preference}`
        ];

        // Agregar rango de edad si existe
        if (request.age_range) {
            parts.push(`Edad ${request.age_range[0]}-${request.age_range[1]} años`);
        }

        // Agregar posición preferida si existe
        if (request.preferred_position) {
            parts.push(`Se busca jugador de ${request.preferred_position}`);
        }

        return parts.join(". ") + ".";
    }

    /**
     * Llamada a OpenAI API para crear embedding
     * @private
     */
    private async createEmbedding(text: string): Promise<number[]> {
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: this.model,
                input: text,
                encoding_format: "float"
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`OpenAI API error: ${error.error?.message || 'Unknown error'}`);
        }

        const data = await response.json();
        return data.data[0].embedding;
    }

    /**
     * Crear embeddings en batch (para optimización)
     */
    async createEmbeddingsBatch(texts: string[]): Promise<number[][]> {
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: this.model,
                input: texts,
                encoding_format: "float"
            })
        });

        if (!response.ok) {
            throw new Error('Batch embedding failed');
        }

        const data = await response.json();
        return data.data.map((item: any) => item.embedding);
    }
}

// ============================================================================
// 🌲 PINECONE VECTOR STORE
// ============================================================================

/**
 * Vector result from Pinecone
 */
interface VectorMatch {
    id: string;
    score: number; // Cosine similarity 0-1
    metadata: PlayerMetadata;
}

/**
 * Metadata almacenada en Pinecone
 */
interface PlayerMetadata {
    name: string;
    elo: number;
    category: Category;
    gender: string;
    age: number;
    zone: string;
    positions: Position[];
}

/**
 * Filtros para búsqueda en Pinecone
 */
interface PineconeFilter {
    [key: string]: any;
}

/**
 * VectorStore - Maneja búsqueda vectorial en Pinecone
 * 
 * Responsabilidades:
 * - Indexar jugadores (upsert)
 * - Buscar similares con filtros
 * - Eliminar jugadores
 */
class VectorStore {
    private apiKey: string;
    private indexName: string;
    private environment: string;
    private indexUrl: string;

    constructor(apiKey: string, indexName: string, environment: string = "us-east-1") {
        this.apiKey = apiKey;
        this.indexName = indexName;
        this.environment = environment;
        this.indexUrl = `https://${indexName}-${environment}.pinecone.io`;
    }

    /**
     * Guardar o actualizar jugador en Pinecone
     * @param playerId - UUID del jugador
     * @param embedding - Vector de 1536 dimensiones
     * @param metadata - Metadata para filtrado
     */
    async upsertPlayer(
        playerId: string,
        embedding: number[],
        metadata: PlayerMetadata
    ): Promise<void> {
        try {
            const response = await fetch(`${this.indexUrl}/vectors/upsert`, {
                method: 'POST',
                headers: {
                    'Api-Key': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    vectors: [{
                        id: playerId,
                        values: embedding,
                        metadata: metadata
                    }]
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(`Pinecone upsert failed: ${error.message}`);
            }

            console.log(`✅ Player ${playerId} indexed successfully`);
        } catch (error) {
            throw new VectorSearchError(`Error upserting player: ${error.message}`);
        }
    }

    /**
     * Upsert en batch (hasta 100 vectores a la vez)
     * @param vectors - Array de vectores con id, values y metadata
     */
    async upsertBatch(vectors: Array<{
        id: string;
        values: number[];
        metadata: PlayerMetadata;
    }>): Promise<void> {
        // Dividir en chunks de 100
        const chunks = this.chunkArray(vectors, 100);

        for (const chunk of chunks) {
            await fetch(`${this.indexUrl}/vectors/upsert`, {
                method: 'POST',
                headers: {
                    'Api-Key': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ vectors: chunk })
            });
        }

        console.log(`✅ ${vectors.length} players indexed in batch`);
    }

    /**
     * Buscar jugadores similares
     * @param queryEmbedding - Vector de consulta (1536 dims)
     * @param filters - Filtros metadata opcionales
     * @param topK - Número de resultados (default: 50)
     * @returns Array de matches ordenados por similitud
     */
    async searchSimilar(
        queryEmbedding: number[],
        filters?: PineconeFilter,
        topK: number = 50
    ): Promise<VectorMatch[]> {
        try {
            const body: any = {
                vector: queryEmbedding,
                topK: topK,
                includeMetadata: true
            };

            if (filters) {
                body.filter = filters;
            }

            const response = await fetch(`${this.indexUrl}/query`, {
                method: 'POST',
                headers: {
                    'Api-Key': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error('Pinecone query failed');
            }

            const data = await response.json();
            
            return data.matches.map((match: any) => ({
                id: match.id,
                score: match.score,
                metadata: match.metadata
            }));
        } catch (error) {
            throw new VectorSearchError(`Error searching similar players: ${error.message}`);
        }
    }

    /**
     * Eliminar jugador del índice
     * @param playerId - UUID del jugador
     */
    async deletePlayer(playerId: string): Promise<void> {
        await fetch(`${this.indexUrl}/vectors/delete`, {
            method: 'POST',
            headers: {
                'Api-Key': this.apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ids: [playerId]
            })
        });

        console.log(`🗑️ Player ${playerId} deleted from index`);
    }

    /**
     * Construir filtros para Pinecone según MatchRequest
     * @param request - Match request con requisitos
     * @returns Objeto de filtros para Pinecone
     */
    buildFilters(request: MatchRequest): PineconeFilter {
        const filters: any = {
            $and: []
        };

        // Filtro por categorías
        if (request.categories.length > 0) {
            filters.$and.push({
                category: { $in: request.categories }
            });
        }

        // Filtro por género (si no es MIXED)
        if (request.gender_preference !== "MIXED") {
            filters.$and.push({
                gender: request.gender_preference
            });
        }

        // Nota: ELO range se filtra después porque Pinecone
        // no optimiza bien los filtros numéricos de rango

        return filters.$and.length > 0 ? filters : undefined;
    }

    /**
     * Utility: dividir array en chunks
     * @private
     */
    private chunkArray<T>(array: T[], size: number): T[][] {
        const chunks: T[][] = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    }
}

// ============================================================================
// 💾 POSTGRESQL DATABASE CLIENT
// ============================================================================

/**
 * Player metrics desde la base de datos
 */
interface PlayerMetrics {
    acceptance_rate: number;
    last_active_days: number;
}

/**
 * DatabaseClient - Maneja consultas a PostgreSQL
 * 
 * Responsabilidades:
 * - Obtener métricas de jugadores (acceptance_rate, last_active_days)
 * - Consultas batch para optimización
 * - Connection pooling
 */
class DatabaseClient {
    private connectionString: string;
    private pool: any; // En Node.js usarías pg.Pool

    constructor(connectionString: string) {
        this.connectionString = connectionString;
        this.initializePool();
    }

    /**
     * Inicializar connection pool
     * @private
     */
    private initializePool(): void {
        // En Node.js con pg:
        // const { Pool } = require('pg');
        // this.pool = new Pool({
        //     connectionString: this.connectionString,
        //     max: 10,
        //     min: 1,
        //     idleTimeoutMillis: 30000
        // });

        console.log('📊 Database pool initialized');
    }

    /**
     * Obtener métricas de un jugador
     * @param playerId - UUID del jugador
     * @returns Métricas comportamentales
     */
    async getPlayerMetrics(playerId: string): Promise<PlayerMetrics> {
        try {
            // Query SQL
            const query = `
                SELECT acceptance_rate, last_active_days
                FROM players
                WHERE id = $1
            `;

            // En Node.js con pg:
            // const result = await this.pool.query(query, [playerId]);
            
            // Simulación para este ejemplo:
            const result = await this.executeQuery(query, [playerId]);

            if (result.rows.length === 0) {
                // Valores por defecto si no existe
                return {
                    acceptance_rate: 0.5,
                    last_active_days: 999
                };
            }

            return {
                acceptance_rate: result.rows[0].acceptance_rate,
                last_active_days: result.rows[0].last_active_days
            };
        } catch (error) {
            throw new DatabaseError(`Error fetching player metrics: ${error.message}`);
        }
    }

    /**
     * Obtener métricas de múltiples jugadores (batch)
     * Optimización: una sola query para todos los jugadores
     * 
     * @param playerIds - Array de UUIDs
     * @returns Map de playerId -> metrics
     */
    async getPlayerMetricsBatch(playerIds: string[]): Promise<Map<string, PlayerMetrics>> {
        try {
            const query = `
                SELECT id, acceptance_rate, last_active_days
                FROM players
                WHERE id = ANY($1)
            `;

            const result = await this.executeQuery(query, [playerIds]);

            const metricsMap = new Map<string, PlayerMetrics>();

            result.rows.forEach((row: any) => {
                metricsMap.set(row.id, {
                    acceptance_rate: row.acceptance_rate,
                    last_active_days: row.last_active_days
                });
            });

            // Agregar valores por defecto para IDs no encontrados
            playerIds.forEach(id => {
                if (!metricsMap.has(id)) {
                    metricsMap.set(id, {
                        acceptance_rate: 0.5,
                        last_active_days: 999
                    });
                }
            });

            return metricsMap;
        } catch (error) {
            throw new DatabaseError(`Error fetching batch metrics: ${error.message}`);
        }
    }

    /**
     * Obtener todos los jugadores (para indexación inicial)
     * @returns Array de todos los jugadores
     */
    async getAllPlayers(): Promise<Player[]> {
        const query = 'SELECT * FROM players ORDER BY elo DESC';
        const result = await this.executeQuery(query, []);

        return result.rows.map((row: any) => this.mapRowToPlayer(row));
    }

    /**
     * Actualizar acceptance_rate de un jugador
     * @param playerId - UUID del jugador
     * @param newRate - Nuevo acceptance rate
     */
    async updateAcceptanceRate(playerId: string, newRate: number): Promise<void> {
        const query = `
            UPDATE players
            SET acceptance_rate = $1, updated_at = NOW()
            WHERE id = $2
        `;

        await this.executeQuery(query, [newRate, playerId]);
        console.log(`✅ Updated acceptance_rate for player ${playerId}: ${newRate}`);
    }

    /**
     * Insertar jugadores en batch (para seeding)
     * @param players - Array de jugadores
     */
    async insertPlayersBatch(players: Player[]): Promise<void> {
        const query = `
            INSERT INTO players (
                id, name, elo, age, gender, category,
                positions, location, availability,
                acceptance_rate, last_active_days
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (id) DO UPDATE SET
                acceptance_rate = EXCLUDED.acceptance_rate,
                last_active_days = EXCLUDED.last_active_days,
                updated_at = NOW()
        `;

        for (const player of players) {
            await this.executeQuery(query, [
                player.id,
                player.name,
                player.elo,
                player.age,
                player.gender,
                player.category,
                JSON.stringify(player.positions),
                JSON.stringify(player.location),
                JSON.stringify(player.availability),
                player.acceptance_rate,
                player.last_active_days
            ]);
        }

        console.log(`✅ Inserted ${players.length} players into database`);
    }

    /**
     * Ejecutar query SQL (wrapper)
     * @private
     */
    private async executeQuery(query: string, params: any[]): Promise<any> {
        // En producción con pg:
        // return await this.pool.query(query, params);
        
        // Simulación para este ejemplo
        console.log(`📊 Executing query: ${query.substring(0, 50)}...`);
        return { rows: [] }; // Mock response
    }

    /**
     * Mapear row de DB a objeto Player
     * @private
     */
    private mapRowToPlayer(row: any): Player {
        return {
            id: row.id,
            name: row.name,
            elo: row.elo,
            age: row.age,
            gender: row.gender,
            category: row.category,
            positions: row.positions,
            location: row.location,
            availability: row.availability,
            acceptance_rate: row.acceptance_rate,
            last_active_days: row.last_active_days
        };
    }

    /**
     * Cerrar pool de conexiones
     */
    async close(): Promise<void> {
        // await this.pool.end();
        console.log('🔒 Database pool closed');
    }
}

// ============================================================================
// 🔧 CONFIGURATION MANAGEMENT
// ============================================================================

/**
 * ConfigManager - Maneja variables de entorno y configuración
 */
class ConfigManager {
    private static instance: ConfigManager;
    private config: AppConfig;

    private constructor() {
        this.config = this.loadConfig();
        this.validateConfig();
    }

    /**
     * Singleton pattern
     */
    static getInstance(): ConfigManager {
        if (!ConfigManager.instance) {
            ConfigManager.instance = new ConfigManager();
        }
        return ConfigManager.instance;
    }

    /**
     * Cargar configuración desde variables de entorno
     * @private
     */
    private loadConfig(): AppConfig {
        return {
            openai_api_key: process.env.OPENAI_API_KEY || '',
            pinecone_api_key: process.env.PINECONE_API_KEY || '',
            pinecone_index_name: process.env.PINECONE_INDEX_NAME || 'matchmaking-players',
            pinecone_environment: process.env.PINECONE_ENVIRONMENT || 'us-east-1',
            database_url: process.env.DATABASE_URL || '',
            log_level: process.env.LOG_LEVEL || 'INFO',
            max_candidates: parseInt(process.env.MAX_CANDIDATES || '50')
        };
    }

    /**
     * Validar que todas las variables requeridas estén presentes
     * @private
     */
    private validateConfig(): void {
        const required = [
            'openai_api_key',
            'pinecone_api_key',
            'database_url'
        ];

        const missing = required.filter(key => !this.config[key as keyof AppConfig]);

        if (missing.length > 0) {
            throw new Error(`Missing required config: ${missing.join(', ')}`);
        }

        console.log('✅ Configuration validated successfully');
    }

    /**
     * Obtener configuración completa
     */
    getConfig(): AppConfig {
        return { ...this.config };
    }

    /**
     * Obtener valor específico de configuración
     */
    get<K extends keyof AppConfig>(key: K): AppConfig[K] {
        return this.config[key];
    }
}

// ============================================================================
// 🔌 DEPENDENCY INJECTION
// ============================================================================

/**
 * ServiceContainer - Maneja instancias singleton de servicios
 */
class ServiceContainer {
    private static embeddingService: EmbeddingService;
    private static vectorStore: VectorStore;
    private static databaseClient: DatabaseClient;

    /**
     * Obtener instancia de EmbeddingService
     */
    static getEmbeddingService(): EmbeddingService {
        if (!this.embeddingService) {
            const config = ConfigManager.getInstance();
            this.embeddingService = new EmbeddingService(
                config.get('openai_api_key')
            );
        }
        return this.embeddingService;
    }

    /**
     * Obtener instancia de VectorStore
     */
    static getVectorStore(): VectorStore {
        if (!this.vectorStore) {
            const config = ConfigManager.getInstance();
            this.vectorStore = new VectorStore(
                config.get('pinecone_api_key'),
                config.get('pinecone_index_name'),
                config.get('pinecone_environment')
            );
        }
        return this.vectorStore;
    }

    /**
     * Obtener instancia de DatabaseClient
     */
    static getDatabaseClient(): DatabaseClient {
        if (!this.databaseClient) {
            const config = ConfigManager.getInstance();
            this.databaseClient = new DatabaseClient(
                config.get('database_url')
            );
        }
        return this.databaseClient;
    }

    /**
     * Limpiar todas las instancias (útil para testing)
     */
    static reset(): void {
        this.embeddingService = null as any;
        this.vectorStore = null as any;
        this.databaseClient = null as any;
    }
}

// ============================================================================
// 📡 MATCHMAKING SERVICE (Orquestación)
// ============================================================================

/**
 * MatchmakingService - Orquesta el proceso completo de matchmaking
 * 
 * Este servicio coordina todos los servicios externos para:
 * 1. Crear embedding del request
 * 2. Buscar similares en Pinecone
 * 3. Aplicar filtros
 * 4. Enriquecer con datos de DB
 * 5. Calcular scoring
 * 6. Retornar top candidatos
 */
class MatchmakingService {
    private embeddingService: EmbeddingService;
    private vectorStore: VectorStore;
    private databaseClient: DatabaseClient;

    constructor(
        embeddingService: EmbeddingService,
        vectorStore: VectorStore,
        databaseClient: DatabaseClient
    ) {
        this.embeddingService = embeddingService;
        this.vectorStore = vectorStore;
        this.databaseClient = databaseClient;
    }

    /**
     * Encontrar candidatos para un partido
     * @param request - Requisitos del partido
     * @returns Top 20 candidatos ordenados por score
     */
    async findCandidates(request: MatchRequest): Promise<Candidate[]> {
        console.log(`🔍 Finding candidates for match ${request.match_id}...`);
        const startTime = Date.now();

        try {
            // PASO 1: Crear embedding del request
            console.log('  [1/6] Creating request embedding...');
            const requestEmbedding = await this.embeddingService.createRequestEmbedding(request);

            // PASO 2: Buscar similares en Pinecone
            console.log('  [2/6] Searching similar players in Pinecone...');
            const filters = this.vectorStore.buildFilters(request);
            const similarPlayers = await this.vectorStore.searchSimilar(
                requestEmbedding,
                filters,
                50
            );

            // PASO 3: Filtrar por ELO range y edad
            console.log('  [3/6] Applying hard filters...');
            const filteredPlayers = this.applyHardFilters(similarPlayers, request);

            // PASO 4: Enriquecer con métricas de DB
            console.log('  [4/6] Enriching with DB metrics...');
            const playerIds = filteredPlayers.map(p => p.id);
            const metricsMap = await this.databaseClient.getPlayerMetricsBatch(playerIds);

            // PASO 5: Calcular scoring
            console.log('  [5/6] Calculating match scores...');
            const candidates = filteredPlayers.map(player => {
                const metrics = metricsMap.get(player.id)!;
                return this.calculateCandidate(player, request, metrics);
            });

            // PASO 6: Ordenar y retornar top 20
            console.log('  [6/6] Sorting and selecting top 20...');
            candidates.sort((a, b) => {
                if (b.score !== a.score) return b.score - a.score;
                return b.acceptance_rate - a.acceptance_rate;
            });

            const topCandidates = candidates.slice(0, 20);

            const elapsed = Date.now() - startTime;
            console.log(`✅ Found ${topCandidates.length} candidates in ${elapsed}ms`);

            return topCandidates;
        } catch (error) {
            console.error(`❌ Error finding candidates: ${error.message}`);
            throw error;
        }
    }

    /**
     * Aplicar filtros obligatorios (ELO, edad)
     * @private
     */
    private applyHardFilters(
        players: VectorMatch[],
        request: MatchRequest
    ): VectorMatch[] {
        return players.filter(player => {
            const metadata = player.metadata;

            // Filtro ELO range
            if (metadata.elo < request.elo_range[0] || metadata.elo > request.elo_range[1]) {
                return false;
            }

            // Filtro edad (si aplica)
            if (request.age_range) {
                if (metadata.age < request.age_range[0] || metadata.age > request.age_range[1]) {
                    return false;
                }
            }

            return true;
        });
    }

    /**
     * Calcular candidato con scoring
     * @private
     */
    private calculateCandidate(
        player: VectorMatch,
        request: MatchRequest,
        metrics: PlayerMetrics
    ): Candidate {
        // Aquí iría el ScoringService completo
        // Por ahora, un ejemplo simplificado:

        const score = player.score * 0.4 + metrics.acceptance_rate * 0.1;
        const eloDiff = Math.abs(player.metadata.elo - (request.elo_range[0] + request.elo_range[1]) / 2);

        const reasons: string[] = [];
        if (player.score > 0.85) reasons.push("Perfil muy compatible");
        if (eloDiff < 100) reasons.push("Nivel muy similar");
        if (metrics.acceptance_rate > 0.8) reasons.push("Alta tasa de aceptación");

        return {
            player_id: player.id,
            player_name: player.metadata.name,
            score: Math.min(1.0, score),
            distance_km: 0, // Calcular con haversine
            elo: player.metadata.elo,
            elo_diff: eloDiff,
            acceptance_rate: metrics.acceptance_rate,
            reasons: reasons,
            invitation_message: `Partido compatible - ${Math.round(score * 100)}% match`,
            compatibility_summary: reasons.join(", ")
        };
    }

    /**
     * Indexar un jugador nuevo
     * @param player - Jugador a indexar
     */
    async indexPlayer(player: Player): Promise<void> {
        console.log(`📝 Indexing player ${player.id}...`);

        // Crear embedding
        const embedding = await this.embeddingService.createPlayerEmbedding(player);

        // Metadata para Pinecone
        const metadata: PlayerMetadata = {
            name: player.name,
            elo: player.elo,
            category: player.category,
            gender: player.gender,
            age: player.age,
            zone: player.location.zone,
            positions: player.positions
        };

        // Guardar en Pinecone
        await this.vectorStore.upsertPlayer(player.id, embedding, metadata);

        console.log(`✅ Player ${player.id} indexed successfully`);
    }
}

// ============================================================================
// 🚀 EJEMPLO DE USO
// ============================================================================

/**
 * Ejemplo completo de uso del sistema
 */
async function exampleUsage() {
    console.log('🚀 Matchmaking AI - Infrastructure Example\n');

    try {
        // 1. Inicializar servicios
        console.log('📦 Initializing services...');
        const embeddingService = ServiceContainer.getEmbeddingService();
        const vectorStore = ServiceContainer.getVectorStore();
        const databaseClient = ServiceContainer.getDatabaseClient();

        const matchmakingService = new MatchmakingService(
            embeddingService,
            vectorStore,
            databaseClient
        );

        // 2. Crear un match request de ejemplo
        const matchRequest: MatchRequest = {
            match_id: "match-123",
            categories: ["SEVENTH", "SIXTH"],
            elo_range: [1400, 1800],
            age_range: [25, 35],
            gender_preference: "MALE",
            required_players: 3,
            location: {
                lat: -31.42647,
                lon: -64.18722,
                zone: "Nueva Córdoba"
            },
            match_time: "19:00",
            required_time: 90,
            preferred_position: "BACKHAND"
        };

        // 3. Buscar candidatos
        console.log('\n🎯 Finding candidates...');
        const candidates = await matchmakingService.findCandidates(matchRequest);

        // 4. Mostrar resultados
        console.log('\n📊 Top Candidates:');
        candidates.slice(0, 5).forEach((candidate, index) => {
            console.log(`\n  ${index + 1}. ${candidate.player_name}`);
            console.log(`     Score: ${candidate.score.toFixed(3)}`);
            console.log(`     ELO: ${candidate.elo} (diff: ${candidate.elo_diff})`);
            console.log(`     Acceptance Rate: ${(candidate.acceptance_rate * 100).toFixed(0)}%`);
            console.log(`     Reasons: ${candidate.reasons.join(', ')}`);
        });

        console.log('\n✅ Example completed successfully!');

    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

// ============================================================================
// 🧪 TESTING UTILITIES
// ============================================================================

/**
 * Función helper para testing
 */
function createMockPlayer(overrides?: Partial<Player>): Player {
    return {
        id: "player-123",
        name: "Juan Pérez",
        elo: 1520,
        age: 28,
        gender: "MALE",
        category: "SEVENTH",
        positions: ["FOREHAND", "BACKHAND"],
        location: {
            lat: -31.42647,
            lon: -64.18722,
            zone: "Nueva Córdoba"
        },
        availability: [
            { min: "18:00", max: "22:00" }
        ],
        acceptance_rate: 0.85,
        last_active_days: 2,
        ...overrides
    };
}

/**
 * Mock de MatchRequest para testing
 */
function createMockMatchRequest(overrides?: Partial<MatchRequest>): MatchRequest {
    return {
        match_id: "match-123",
        categories: ["SEVENTH", "SIXTH"],
        elo_range: [1400, 1800],
        gender_preference: "MALE",
        required_players: 3,
        location: {
            lat: -31.42647,
            lon: -64.18722,
            zone: "Nueva Córdoba"
        },
        match_time: "19:00",
        required_time: 90,
        ...overrides
    };
}

// ============================================================================
// ❌ CUSTOM ERRORS
// ============================================================================

class EmbeddingError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'EmbeddingError';
    }
}

class VectorSearchError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'VectorSearchError';
    }
}

class DatabaseError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'DatabaseError';
    }
}

// ============================================================================
// 📝 DOCUMENTATION & CHECKLIST
// ============================================================================

/**
 * 🎯 CHECKLIST DE IMPLEMENTACIÓN
 * 
 * [ ] OpenAI Embeddings Service
 *     [ ] EmbeddingService class
 *     [ ] createPlayerEmbedding()
 *     [ ] createRequestEmbedding()
 *     [ ] buildPlayerDescription()
 *     [ ] buildRequestDescription()
 *     [ ] Error handling y retries
 * 
 * [ ] Pinecone Vector Store
 *     [ ] VectorStore class
 *     [ ] upsertPlayer()
 *     [ ] upsertBatch()
 *     [ ] searchSimilar()
 *     [ ] deletePlayer()
 *     [ ] buildFilters()
 * 
 * [ ] PostgreSQL Database Client
 *     [ ] DatabaseClient class
 *     [ ] Connection pooling
 *     [ ] getPlayerMetrics()
 *     [ ] getPlayerMetricsBatch()
 *     [ ] getAllPlayers()
 *     [ ] updateAcceptanceRate()
 *     [ ] insertPlayersBatch()
 * 
 * [ ] Configuration & DI
 *     [ ] ConfigManager singleton
 *     [ ] ServiceContainer
 *     [ ] Environment variables
 *     [ ] Validation
 * 
 * [ ] Integration
 *     [ ] MatchmakingService
 *     [ ] Pipeline completo (6 pasos)
 *     [ ] Error handling
 *     [ ] Performance logging
 * 
 * [ ] Testing
 *     [ ] Unit tests
 *     [ ] Integration tests
 *     [ ] Mock utilities
 *     [ ] Performance tests
 */

/**
 * ⚡ PERFORMANCE TARGETS
 * 
 * OpenAI embedding:     < 100ms
 * Pinecone search:      < 50ms
 * PostgreSQL batch:     < 30ms
 * Total pipeline:       < 200ms
 */

/**
 * 🔑 ENVIRONMENT VARIABLES REQUIRED
 * 
 * OPENAI_API_KEY=sk-proj-...
 * PINECONE_API_KEY=pcsk_...
 * PINECONE_INDEX_NAME=matchmaking-players
 * PINECONE_ENVIRONMENT=us-east-1
 * DATABASE_URL=postgresql://user:pass@localhost:5432/pader_mock
 * LOG_LEVEL=INFO
 * MAX_CANDIDATES=50
 */

// ============================================================================
// 🎉 EXPORT ALL
// ============================================================================

export {
    // Types
    Player,
    MatchRequest,
    Candidate,
    Category,
    Position,
    Location,
    TimeSlot,
    PlayerMetadata,
    PlayerMetrics,
    AppConfig,
    
    // Services
    EmbeddingService,
    VectorStore,
    DatabaseClient,
    MatchmakingService,
    
    // Infrastructure
    ConfigManager,
    ServiceContainer,
    
    // Utilities
    createMockPlayer,
    createMockMatchRequest,
    
    // Errors
    EmbeddingError,
    VectorSearchError,
    DatabaseError
};

console.log('✅ Infrastructure guide loaded successfully!');

