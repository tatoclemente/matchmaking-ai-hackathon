from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
from src.config import config

class PineconeClient:
    def __init__(self):
        self.pc = None
        self.index_name = config.PINECONE_INDEX_NAME
        self.index = None
    
    def _get_client(self):
        if self.pc is None:
            self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        return self.pc
    
    def initialize_index(self):
        """Crear índice si no existe y conectar"""
        pc = self._get_client()
        if self.index_name not in pc.list_indexes().names():
            pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    model="text-embedding-3-small",
                    region=config.PINECONE_ENVIRONMENT
                )
            )
        
        self.index = self._get_client().Index(self.index_name)
        return self.index
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """Insertar vectores con metadata"""
        if not self.index:
            self.initialize_index()
        
        self.index.upsert(vectors=vectors)
    
    def search_similar(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """Buscar vectores similares"""
        if not self.index:
            self.initialize_index()
        
        results = self.index.query(
            vector=query_embedding,
            filter=filters,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches

pinecone_client = PineconeClient()
