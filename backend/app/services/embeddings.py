"""Embedding generation service using OpenAI."""

from typing import List
import numpy as np
from openai import OpenAI
import os

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingsService:
    """Generates embeddings using OpenAI's API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize embeddings service.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
        self.dimension = 1536
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            Numpy array of shape (len(texts), 1536)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            logger.info(f"Generated embeddings with shape: {embeddings_array.shape}")
            return embeddings_array
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            Numpy array of shape (1536,)
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0]
