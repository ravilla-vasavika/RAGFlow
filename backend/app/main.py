"""FastAPI application entrypoint with lifespan management."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import upload, query, documents
from app.utils.logger import setup_logger
from app.utils.db import DatabaseManager
from app.services.vector_store import FAISSVectorStore
from app.services.embeddings import EmbeddingsService
from app.services.llm import OpenAILLM

# Load environment variables before anything else
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    All shared services are initialized once here and attached to app.state
    so route handlers can access them without re-initializing per request.
    """
    logger.info("=" * 50)
    logger.info("Starting DocuMind Backend")
    logger.info("=" * 50)

    # --- Validate required environment variables ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("CRITICAL: OPENAI_API_KEY not set in environment")
        raise RuntimeError("OPENAI_API_KEY must be set in .env file")

    logger.info("✓ Environment variables loaded")
    logger.info(f"  - CHUNK_SIZE:      {os.getenv('CHUNK_SIZE', 512)}")
    logger.info(f"  - CHUNK_OVERLAP:   {os.getenv('CHUNK_OVERLAP', 50)}")
    logger.info(f"  - TOP_K_RESULTS:   {os.getenv('TOP_K_RESULTS', 5)}")
    logger.info(f"  - MAX_PDF_SIZE_MB: {os.getenv('MAX_PDF_SIZE_MB', 20)}")

    # --- Initialize database ---
    try:
        db_path = os.getenv("DATABASE_PATH", "./data/metadata.db")
        app.state.db = DatabaseManager(db_path=db_path)
        logger.info(f"✓ Database initialized at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # --- Initialize vector store ---
    try:
        vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/faiss_index")
        app.state.vector_store = FAISSVectorStore(index_path=vector_store_path)
        logger.info(f"✓ Vector store initialized at {vector_store_path}")
        logger.info(f"  - Vectors in index: {app.state.vector_store.get_doc_count()}")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise

    # --- Initialize embeddings service ---
    try:
        app.state.embeddings_service = EmbeddingsService()
        logger.info("✓ Embeddings service initialized (text-embedding-3-small)")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings service: {e}")
        raise

    # --- Initialize LLM service ---
    try:
        app.state.llm = OpenAILLM()
        logger.info("✓ LLM service initialized (gpt-4o-mini)")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        raise

    logger.info("=" * 50)
    logger.info("All services ready — application startup complete")
    logger.info("=" * 50)

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("=" * 50)
    logger.info("Shutting down DocuMind Backend")
    logger.info("=" * 50)


# --- Create FastAPI app ---
app = FastAPI(
    title="DocuMind API",
    description="Retrieval-Augmented Generation backend using FAISS and OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS middleware ---
# Must be added immediately after app creation and before routers
# so preflight OPTIONS requests are handled before hitting any route
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",  # Some browsers use 127.0.0.1 instead of localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register routers ---
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(documents.router)


@app.get("/health")
async def health_check():
    """Health check — also returns live service stats."""
    return {
        "status": "healthy",
        "service": "DocuMind API",
        "vectors_in_index": app.state.vector_store.get_doc_count()
    }


@app.get("/")
async def root():
    """Root endpoint — API overview."""
    return {
        "message": "Welcome to DocuMind API",
        "docs": "/docs",
        "endpoints": {
            "health":          "/health",
            "upload_pdf":      "/api/upload_pdf",
            "query":           "/api/query",
            "list_documents":  "/api/list_documents",
            "delete_document": "/api/document/{document_id}",
            "rebuild_index":   "/api/rebuild_index"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )