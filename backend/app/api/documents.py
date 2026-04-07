"""Document management endpoints."""

from fastapi import APIRouter, HTTPException, Request
import os

from app.models.schemas import ListDocumentsResponse, DeleteResponse, DocumentInfo, RebuildIndexResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/list_documents", response_model=ListDocumentsResponse)
async def list_documents(request: Request):
    """
    List all active (non-deleted) documents.
    Returns document_id, filename, upload timestamp, and chunk count.
    """
    try:
        logger.info("Listing documents")

        db = request.app.state.db  # ← shared instance
        documents = db.get_all_documents()

        document_infos = [
            DocumentInfo(
                document_id=doc["document_id"],
                filename=doc["filename"],
                upload_timestamp=doc["upload_timestamp"],
                chunk_count=doc["chunk_count"]
            )
            for doc in documents
        ]

        logger.info(f"Found {len(document_infos)} documents")
        return ListDocumentsResponse(documents=document_infos)

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.delete("/document/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str, request: Request):
    """
    Soft-delete a document and rebuild the FAISS index to exclude it.
    Returns 404 if document does not exist.
    """
    try:
        logger.info(f"Deleting document: {document_id}")

        db = request.app.state.db                      # ← shared instance
        vector_store = request.app.state.vector_store  # ← shared instance

        # Check document exists
        if not db.document_exists(document_id):
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found or already deleted"
            )

        # Soft-delete in SQLite
        try:
            db.soft_delete_document(document_id)
        except Exception as e:
            logger.error(f"Database deletion error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document from database"
            )

        # Mark deleted in shared vector store and physically rebuild index
        try:
            vector_store.delete_document(document_id)
            vector_store.rebuild_index()
            logger.info("Vector index rebuilt after deletion")
        except Exception as e:
            logger.error(f"Vector store rebuild error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to rebuild vector index"
            )

        logger.info(f"Successfully deleted document: {document_id}")
        return DeleteResponse(
            message="Document deleted successfully",
            document_id=document_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting document: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/rebuild_index", response_model=RebuildIndexResponse)
async def rebuild_faiss_index(request: Request):
    """
    Rebuild the FAISS index from SQLite chunks.

    Re-embeds all active chunks from the database and rebuilds the FAISS
    index from scratch. Use this to fix any sync issues between SQLite
    and the vector store.
    """
    try:
        logger.info("Starting FAISS index rebuild from database...")

        db = request.app.state.db                            # ← shared instance
        vector_store = request.app.state.vector_store        # ← shared instance
        embeddings_service = request.app.state.embeddings_service  # ← shared instance

        # Get all active documents
        documents = db.get_all_documents()
        if not documents:
            logger.warning("No active documents found — nothing to rebuild")
            return RebuildIndexResponse(
                message="No active documents to rebuild",
                chunks_reindexed=0
            )

        # Collect all chunk texts and metadata from SQLite
        all_texts = []
        all_metadatas = []

        for doc in documents:
            doc_id = doc["document_id"]
            chunks = db.get_chunks_by_doc_id(doc_id)

            for chunk in chunks:
                all_texts.append(chunk["chunk_text"])
                all_metadatas.append({
                    "document_id": doc_id,
                    "filename": doc["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_text": chunk["chunk_text"]
                })

        logger.info(f"Re-embedding {len(all_texts)} chunks from SQLite...")

        # Re-generate embeddings for all active chunks
        embeddings = embeddings_service.generate_embeddings(all_texts)

        # Reset the shared FAISS index completely
        import faiss
        import numpy as np

        vector_store.index = faiss.IndexFlatL2(vector_store.dimension)
        vector_store.metadatas = []
        vector_store.deleted_ids = set()

        # Add all fresh embeddings to the reset index
        vector_store.add_documents(embeddings, all_metadatas)

        logger.info(f"Rebuild complete — {len(all_texts)} chunks reindexed")

        return RebuildIndexResponse(
            message="FAISS index rebuilt successfully",
            chunks_reindexed=len(all_texts)
        )

    except Exception as e:
        logger.error(f"Error rebuilding FAISS index: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rebuild index: {str(e)}"
        )