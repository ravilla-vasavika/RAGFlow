"""Document retrieval service using vector similarity search."""

from typing import List, Optional
import numpy as np

from app.services.vector_store import FAISSVectorStore
from app.services.embeddings import EmbeddingsService
from app.models.schemas import RetrievedChunk
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RetrievalService:
    """Handles document retrieval using vector similarity search."""

    def __init__(
        self,
        vector_store: FAISSVectorStore,
        embeddings_service: EmbeddingsService,
        top_k: int = 5
    ):
        """
        Initialize retrieval service.

        Args:
            vector_store: Shared vector store instance
            embeddings_service: Shared embeddings service instance
            top_k: Default number of results to retrieve
        """
        self.vector_store = vector_store
        self.embeddings_service = embeddings_service
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query using vector similarity search.

        Args:
            query: Natural language search query
            document_ids: If provided, restrict search to these document IDs only
            top_k: Override default number of results

        Returns:
            List of RetrievedChunk objects sorted by similarity score descending
        """
        top_k = top_k or self.top_k

        logger.info(f"Retrieving top {top_k} chunks for query: {query[:50]}...")

        # Validate document_ids if provided
        if document_ids is not None and len(document_ids) == 0:
            logger.warning("Empty document_ids list provided — returning no results")
            return []

        # Generate query embedding
        try:
            query_embedding = self.embeddings_service.generate_single_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise

        # Validate embedding shape
        query_embedding = np.asarray(query_embedding, dtype=np.float32)
        if query_embedding.ndim != 1:
            raise ValueError(
                f"Expected 1D query embedding, got shape: {query_embedding.shape}"
            )

        # Search vector store with optional document ID filter
        try:
            results = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_doc_ids=document_ids
            )
        except Exception as e:
            logger.error(f"Vector store search failed: {e}")
            raise

        # Map raw results to typed RetrievedChunk objects
        retrieved_chunks = []
        for similarity_score, metadata in results:
            # Guard against malformed metadata entries
            if not all(k in metadata for k in ("document_id", "filename", "chunk_index", "chunk_text")):
                logger.warning(f"Skipping malformed metadata entry: {metadata}")
                continue

            chunk = RetrievedChunk(
                document_id=metadata["document_id"],
                filename=metadata["filename"],
                chunk_index=metadata["chunk_index"],
                chunk_text=metadata["chunk_text"],
                similarity_score=float(similarity_score)
            )
            retrieved_chunks.append(chunk)

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
        return retrieved_chunks