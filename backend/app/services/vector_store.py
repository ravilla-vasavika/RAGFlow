"""Vector store abstraction layer for document embeddings."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
import numpy as np
import pickle
from pathlib import Path

try:
    import faiss
except ImportError:
    raise ImportError("faiss-cpu not installed. Run: pip install faiss-cpu")

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations."""

    @abstractmethod
    def add_documents(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Add document embeddings to the store."""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_doc_ids: Optional[List[str]] = None,
    ) -> List[Tuple[float, Dict]]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Soft-delete a document from the store."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persist the vector store to disk."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load the vector store from disk."""
        pass


class FAISSVectorStore(VectorStoreBase):
    """FAISS-based vector store implementation with soft-delete and rebuild support."""

    def __init__(self, index_path: str = "./data/faiss_index", dimension: int = 1536):
        """
        Initialize FAISS vector store.

        Args:
            index_path: Directory path to persist FAISS index files
            dimension: Embedding dimension (text-embedding-3-small default is 1536)
        """
        self.index_path = Path(index_path)
        
        # Ensure directory exists with explicit error handling
        try:
            self.index_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"FAISS index directory ready at {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to create FAISS index directory: {e}")
            raise
        
        self.dimension = dimension
        self.index = None
        self.metadatas: List[Dict] = []
        self.deleted_ids: set = set()

        # Load existing index or create a fresh one
        if self._index_file_exists():
            self.load()
        else:
            self.index = faiss.IndexFlatL2(dimension)

    def _index_file_exists(self) -> bool:
        """Check if persisted index files exist on disk."""
        return (self.index_path / "index.faiss").exists()

    def add_documents(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """
        Add document embeddings to the store incrementally.

        Args:
            embeddings: Array of shape (n_docs, dimension)
            metadatas: Metadata dict for each embedding (must match length)
        """
        if embeddings.size == 0:
            logger.warning("add_documents called with empty embeddings — skipping")
            return

        embeddings = np.asarray(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings)  # Normalize for cosine-like L2 search

        self.index.add(embeddings)
        self.metadatas.extend(metadatas)

        logger.info(f"Added {len(metadatas)} chunks to vector store")
        self.save()

    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_doc_ids: Optional[List[str]] = None,
    ) -> List[Tuple[float, Dict]]:
        """
        Search for similar chunks, filtering out deleted docs and scoping by doc_ids.

        Args:
            query_embedding: 1D query embedding vector
            top_k: Number of results to return after filtering
            filter_doc_ids: If provided, restrict results to these document IDs only

        Returns:
            List of (similarity_score, metadata) tuples, sorted by score descending
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Similarity search called on empty vector store")
            return []

        # Normalize query vector
        query_embedding = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        # Search broader pool to account for deleted/filtered chunks
        search_k = min(top_k * 10, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, search_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # FAISS returns -1 for unfilled slots
            if idx == -1 or idx >= len(self.metadatas):
                continue

            metadata = self.metadatas[idx]
            doc_id = metadata.get("document_id")

            # Skip soft-deleted documents
            if doc_id in self.deleted_ids:
                continue

            # Scope to specified document IDs if provided
            if filter_doc_ids and doc_id not in filter_doc_ids:
                continue

            # Convert L2 distance to a 0–1 similarity score
            similarity_score = float(1 / (1 + distance))
            results.append((similarity_score, metadata))

            if len(results) >= top_k:
                break

        logger.info(f"Similarity search returned {len(results)} results")
        return results

    def delete_document(self, document_id: str) -> None:
        """
        Soft-delete a document by marking its ID for filtering.

        Args:
            document_id: UUID of the document to delete
        """
        self.deleted_ids.add(document_id)
        logger.info(f"Soft-deleted document: {document_id}")

    def rebuild_index(self) -> None:
        """
        Physically rebuild the FAISS index, permanently removing soft-deleted chunks.

        Uses IndexFlatL2.reconstruct() to recover stored vectors without needing
        to re-embed. Safe to call after any deletion operation.
        """
        logger.info("Starting FAISS index rebuild...")

        active_embeddings = []
        active_metadatas = []

        for i, meta in enumerate(self.metadatas):
            if meta.get("document_id") in self.deleted_ids:
                continue  # Skip deleted chunks

            # Reconstruct the stored embedding vector from the FAISS index
            embedding = np.zeros(self.dimension, dtype=np.float32)
            self.index.reconstruct(i, embedding)
            active_embeddings.append(embedding)
            active_metadatas.append(meta)

        # Reset to a clean index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadatas = []
        self.deleted_ids = set()  # Cleared — deletions are now physical

        if active_embeddings:
            embeddings_array = np.array(active_embeddings, dtype=np.float32)
            self.index.add(embeddings_array)
            self.metadatas = active_metadatas

        self.save()
        logger.info(f"Index rebuild complete. Active chunks: {len(self.metadatas)}")

    def save(self) -> None:
        """Persist the FAISS index and metadata to disk."""
        try:
            # Ensure directory exists before writing
            self.index_path.mkdir(parents=True, exist_ok=True)
            
            faiss.write_index(self.index, str(self.index_path / "index.faiss"))
            with open(self.index_path / "metadata.pkl", "wb") as f:
                pickle.dump(
                    {"metadatas": self.metadatas, "deleted_ids": self.deleted_ids}, f
                )
            logger.info(f"Vector store persisted to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise

    def load(self) -> None:
        """Load the FAISS index and metadata from disk."""
        try:
            self.index = faiss.read_index(str(self.index_path / "index.faiss"))
            with open(self.index_path / "metadata.pkl", "rb") as f:
                data = pickle.load(f)
            self.metadatas = data.get("metadatas", [])
            self.deleted_ids = data.get("deleted_ids", set())
            logger.info(
                f"Vector store loaded — {self.index.ntotal} vectors, "
                f"{len(self.deleted_ids)} soft-deleted"
            )
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def get_doc_count(self) -> int:
        """Return total number of vectors currently in the index."""
        return self.index.ntotal if self.index else 0