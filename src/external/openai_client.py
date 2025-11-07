from openai import OpenAI
from typing import List
from src.config import config

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
    
    def create_embedding(self, text: str) -> List[float]:
        """Crear embedding para un texto"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Crear embeddings en batch (hasta 100 textos)"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )
        return [item.embedding for item in response.data]

openai_client = OpenAIClient()
