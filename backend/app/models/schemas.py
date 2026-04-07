"""Pydantic models for request/response validation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A retrieved chunk from the vector store."""
    document_id: str
    filename: str
    chunk_index: int
    chunk_text: str
    similarity_score: float


class UploadResponse(BaseModel):
    """Response for PDF upload."""
    document_id: str
    filename: str
    chunks_created: int
    message: str


class QueryRequest(BaseModel):
    """Request for RAG query."""
    query: str = Field(..., description="The question to answer")
    document_ids: Optional[List[str]] = Field(
        None,
        description="Optional list of document IDs to scope the search"
    )
    top_k: Optional[int] = Field(
        None,
        description="Optional number of top results to retrieve"
    )


class QueryResponse(BaseModel):
    """Response for RAG query."""
    answer: str
    retrieved_chunks: List[RetrievedChunk]


class DocumentInfo(BaseModel):
    """Information about a document."""
    document_id: str
    filename: str
    upload_timestamp: str
    chunk_count: int


class ListDocumentsResponse(BaseModel):
    """Response for listing documents."""
    documents: List[DocumentInfo]


class DeleteResponse(BaseModel):
    """Response for document deletion."""
    message: str
    document_id: str


class RebuildIndexResponse(BaseModel):
    """Response for FAISS index rebuild."""
    message: str
    chunks_reindexed: int


class ErrorResponse(BaseModel):
    """Structured error response."""
    detail: str
    status_code: int