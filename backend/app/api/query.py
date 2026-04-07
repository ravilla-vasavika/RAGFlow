"""RAG query endpoint."""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
import asyncio
import os

from app.models.schemas import QueryRequest, QueryResponse
from app.services.retrieval import RetrievalService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(request_body: QueryRequest, request: Request):
    """
    Query documents using RAG (Retrieval-Augmented Generation).

    - Retrieves relevant chunks from vector store using similarity search
    - Constructs grounded prompt with retrieved context
    - Sends to LLM for answer generation
    - Returns both the answer and source chunks for transparency
    """
    top_k = request_body.top_k or int(os.getenv("TOP_K_RESULTS", 5))

    logger.info(f"Processing query: {request_body.query[:50]}...")

    # Reuse shared service instances initialized at app startup (no per-request re-init)
    vector_store = request.app.state.vector_store
    embeddings_service = request.app.state.embeddings_service
    llm = request.app.state.llm

    # Initialize retrieval service (lightweight — just wires dependencies)
    try:
        retrieval_service = RetrievalService(
            vector_store=vector_store,
            embeddings_service=embeddings_service,
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"Service initialization error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize retrieval service"
        )

    # Retrieve relevant chunks from vector store
    try:
        retrieved_chunks = retrieval_service.retrieve(
            query=request_body.query,
            document_ids=request_body.document_ids,
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve documents"
        )

    # Return fallback if no relevant chunks found
    if not retrieved_chunks:
        logger.info("No relevant chunks found for query")
        return QueryResponse(
            answer="I could not find relevant information in the selected documents.",
            retrieved_chunks=[]
        )

    # Build context string — label each chunk with its source for traceability
    context = "\n\n".join([
        f"[{chunk.filename} - Chunk {chunk.chunk_index}]\n{chunk.chunk_text}"
        for chunk in retrieved_chunks
    ])

    logger.debug(f"Context length: {len(context)} chars, chunks: {len(retrieved_chunks)}")

    # Run blocking OpenAI call in thread pool — avoids blocking the async event loop
    try:
        answer = await asyncio.get_event_loop().run_in_executor(
            None, llm.generate_answer, context, request_body.query
        )
        logger.info("Answer generated successfully")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer"
        )

    return QueryResponse(
        answer=answer,
        retrieved_chunks=retrieved_chunks
    )