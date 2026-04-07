"""PDF upload endpoint."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from uuid import uuid4
import os
import tempfile

from app.models.schemas import UploadResponse
from app.services.ingestion import IngestionService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload_pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    request: Request = None
):
    """
    Upload and process a PDF file.

    - Validates PDF format and size
    - Extracts text using pdfplumber
    - Splits into chunks
    - Generates embeddings using shared embeddings service
    - Stores in shared FAISS instance and SQLite
    """
    temp_file_path = None

    # Load config from environment
    chunk_size = int(os.getenv("CHUNK_SIZE", 512))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
    max_pdf_size = int(os.getenv("MAX_PDF_SIZE_MB", 20))

    # Pull shared service instances from app.state
    # These are initialized once at startup in main.py lifespan
    db = request.app.state.db
    vector_store = request.app.state.vector_store
    embeddings_service = request.app.state.embeddings_service

    try:
        # --- Validate file type ---
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only PDF files are accepted."
            )

        # --- Duplicate filename guard ---
        # Prevent the same PDF being uploaded multiple times creating UUID mismatches
        existing_docs = db.get_all_documents()
        for doc in existing_docs:
            if doc["filename"] == file.filename:
                raise HTTPException(
                    status_code=409,
                    detail=f"'{file.filename}' is already uploaded. Delete it first before re-uploading."
                )

        # --- Write to temp file for processing ---
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        contents = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # --- Validate file size ---
        try:
            IngestionService.validate_pdf_file(temp_file_path, max_pdf_size)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # --- Extract and chunk text ---
        ingestion_service = IngestionService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        try:
            chunks = ingestion_service.process_pdf(temp_file_path)
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse PDF: {str(e)}"
            )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from this PDF. It may be scanned or image-based."
            )

        # --- Generate embeddings using shared service ---
        try:
            embeddings = embeddings_service.generate_embeddings(chunks)
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate embeddings"
            )

        # --- Store in shared FAISS instance and SQLite ---
        document_id = str(uuid4())

        try:
            # Build metadata for each chunk
            metadatas = [
                {
                    "document_id": document_id,
                    "filename": file.filename,
                    "chunk_index": i,
                    "chunk_text": chunk
                }
                for i, chunk in enumerate(chunks)
            ]

            # Add to shared FAISS vector store (incremental — does not overwrite)
            vector_store.add_documents(embeddings, metadatas)

            # Persist document and chunks to SQLite
            db.insert_document(document_id, file.filename, len(chunks))
            db.insert_chunks(document_id, chunks)

            logger.info(f"Successfully processed document: {document_id}")

            return UploadResponse(
                document_id=document_id,
                filename=file.filename,
                chunks_created=len(chunks),
                message="PDF uploaded and processed successfully"
            )

        except Exception as e:
            logger.error(f"Storage error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to store document embeddings"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
    finally:
        # Always clean up temp file regardless of success or failure
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass