# RAG Flow Backend

A Retrieval-Augmented Generation (RAG) backend built with FastAPI, FAISS, and OpenAI. This service enables document uploading, intelligent retrieval, and AI-powered question answering.

## Features

- **PDF Upload & Ingestion**: Upload PDFs with automatic text extraction and chunking
- **Vector Search**: Fast semantic search using FAISS with OpenAI embeddings
- **RAG Pipeline**: Retrieve relevant documents and generate answers using GPT-4o-mini
- **Document Management**: List and delete documents with soft-delete support
- **Persistent Storage**: SQLite metadata and FAISS vector index persistence
- **Structured Logging**: Comprehensive logging to console and rotating files
- **Error Handling**: Detailed error responses with appropriate HTTP status codes

## Tech Stack

- **FastAPI**: Modern async web framework
- **FAISS**: Vector similarity search and clustering
- **OpenAI**: text-embedding-3-small for embeddings, gpt-4o-mini for LLM
- **pdfplumber**: PDF text extraction
- **SQLite**: Metadata persistence
- **Langchain**: Text splitting and chunking

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── upload.py      # PDF upload endpoint
│   │   ├── query.py       # RAG query endpoint
│   │   └── documents.py   # Document management endpoints
│   ├── services/
│   │   ├── ingestion.py   # PDF parsing and chunking
│   │   ├── embeddings.py  # Embedding generation
│   │   ├── vector_store.py # FAISS abstraction
│   │   ├── retrieval.py   # Semantic search
│   │   └── llm.py         # LLM integration
│   ├── models/
│   │   └── schemas.py     # Pydantic request/response models
│   ├── utils/
│   │   ├── logger.py      # Centralized logging
│   │   └── db.py          # SQLite helper functions
│   └── main.py            # FastAPI app entrypoint
├── data/                  # Vector store and database (created at runtime)
├── logs/                  # Application logs
├── .env                   # Environment configuration
├── requirements.txt       # Python dependencies
└── .gitignore
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file with your settings:

```env
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (defaults shown)
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
MAX_PDF_SIZE_MB=20
DATABASE_PATH=./data/metadata.db
VECTOR_STORE_PATH=./data/faiss_index
LOG_LEVEL=INFO
```

### 4. Run the Application

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`

Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Health Check
```http
GET /health
```

### Upload PDF
```http
POST /api/upload_pdf
Content-Type: multipart/form-data

file: <pdf_file>
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "report.pdf",
  "chunks_created": 42,
  "message": "PDF uploaded and processed successfully"
}
```

### Query Documents (RAG)
```http
POST /api/query
Content-Type: application/json

{
  "query": "What is the refund policy?",
  "document_ids": ["uuid1", "uuid2"],  // Optional
  "top_k": 5                            // Optional
}
```

**Response:**
```json
{
  "answer": "The refund policy allows...",
  "retrieved_chunks": [
    {
      "document_id": "uuid",
      "filename": "policy.pdf",
      "chunk_index": 3,
      "chunk_text": "...",
      "similarity_score": 0.87
    }
  ]
}
```

### List Documents
```http
GET /api/list_documents
```

**Response:**
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "report.pdf",
      "upload_timestamp": "2025-01-01T12:00:00Z",
      "chunk_count": 42
    }
  ]
}
```

### Delete Document
```http
DELETE /api/document/{document_id}
```

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": "uuid"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `CHUNK_SIZE` | 512 | Text chunk size in tokens |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks in tokens |
| `TOP_K_RESULTS` | 5 | Default number of retrieved results |
| `MAX_PDF_SIZE_MB` | 20 | Maximum PDF file size |
| `DATABASE_PATH` | `./data/metadata.db` | SQLite database location |
| `VECTOR_STORE_PATH` | `./data/faiss_index` | FAISS index location |
| `LOG_LEVEL` | `INFO` | Logging level |

## Database Schema

### documents
```sql
CREATE TABLE documents (
  document_id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  upload_timestamp TEXT NOT NULL,
  total_chunks INTEGER NOT NULL
)
```

### chunks
```sql
CREATE TABLE chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  FOREIGN KEY(document_id) REFERENCES documents(document_id)
)
```

### deleted_documents
```sql
CREATE TABLE deleted_documents (
  document_id TEXT PRIMARY KEY,
  deleted_at TEXT NOT NULL
)
```

## Logging

Logs are written to:
- **Console**: Real-time output during execution
- **File**: `logs/app.log` with rotation (10 MB max, 5 backups)

Log format: `TIMESTAMP - LOGGER - LEVEL - MESSAGE`

## Error Handling

The API returns structured error responses:

```json
{
  "detail": "Error description"
}
```

Common status codes:
- `200`: Success
- `400`: Bad request (invalid PDF, wrong file type, etc.)
- `404`: Document not found
- `500`: Server error (embedding failure, database error, etc.)

## Performance Considerations

- **Vector Search**: O(log n) with FAISS
- **Chunking**: Configurable chunk size affects accuracy vs. performance tradeoff
- **Embeddings**: Batch processing for efficiency
- **Scaling**: FAISS supports millions of vectors in memory

## Development

### Code Style
- Follows PEP 8
- Type hints throughout
- Comprehensive docstrings

### Adding New Features
1. Create service in `app/services/`
2. Define Pydantic models in `app/models/schemas.py`
3. Add endpoints in `app/api/`
4. Include in `app/main.py`

## Troubleshooting

### OPENAI_API_KEY not set
```
ERROR: CRITICAL: OPENAI_API_KEY not set in environment
```
**Solution**: Add `OPENAI_API_KEY` to `.env` file

### PDF parsing error
```
ERROR: Failed to parse PDF: [error message]
```
**Solution**: Ensure PDF is valid and not corrupted

### FAISS index not found
On first run, the FAISS index will be created automatically. The `data/` directory must be writable.

### Memory issues with large PDFs
Increase `CHUNK_SIZE` to reduce number of chunks and embeddings generated.

## License

MIT

## Support

For issues or questions, please refer to the API documentation at `/docs`
