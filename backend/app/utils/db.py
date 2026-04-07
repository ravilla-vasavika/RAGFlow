"""SQLite database utilities for metadata persistence."""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for RAG metadata."""
    
    def __init__(self, db_path: str = "./data/metadata.db"):
        """
        Initialize database manager and create tables if needed.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_timestamp TEXT NOT NULL,
                    total_chunks INTEGER NOT NULL
                )
            """)
            
            # Chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id)
                )
            """)
            
            # Deleted documents tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deleted_documents (
                    document_id TEXT PRIMARY KEY,
                    deleted_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
            raise
        finally:
            conn.close()
    
    def insert_document(self, document_id: str, filename: str, 
                       total_chunks: int) -> None:
        """
        Insert document metadata.
        
        Args:
            document_id: Unique document identifier
            filename: Original filename
            total_chunks: Number of chunks created from this document
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO documents (document_id, filename, upload_timestamp, total_chunks)
                VALUES (?, ?, ?, ?)
            """, (
                document_id,
                filename,
                datetime.utcnow().isoformat() + "Z",
                total_chunks
            ))
            conn.commit()
            logger.info(f"Inserted document: {document_id} ({filename})")
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
        finally:
            conn.close()
    
    def insert_chunks(self, document_id: str, chunks: List[str]) -> None:
        """
        Insert text chunks for a document.
        
        Args:
            document_id: Document identifier
            chunks: List of chunk texts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            for chunk_index, chunk_text in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO chunks (document_id, chunk_index, chunk_text)
                    VALUES (?, ?, ?)
                """, (document_id, chunk_index, chunk_text))
            
            conn.commit()
            logger.info(f"Inserted {len(chunks)} chunks for document: {document_id}")
        except Exception as e:
            logger.error(f"Error inserting chunks: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all active (non-deleted) documents."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT d.document_id, d.filename, d.upload_timestamp, d.total_chunks
                FROM documents d
                LEFT JOIN deleted_documents dd ON d.document_id = dd.document_id
                WHERE dd.document_id IS NULL
                ORDER BY d.upload_timestamp DESC
            """)
            
            rows = cursor.fetchall()
            documents = [
                {
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "upload_timestamp": row["upload_timestamp"],
                    "chunk_count": row["total_chunks"]
                }
                for row in rows
            ]
            return documents
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise
        finally:
            conn.close()
    
    def get_chunks_by_doc_id(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT document_id, chunk_index, chunk_text
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index
            """, (document_id,))
            
            rows = cursor.fetchall()
            chunks = [
                {
                    "document_id": row["document_id"],
                    "chunk_index": row["chunk_index"],
                    "chunk_text": row["chunk_text"]
                }
                for row in rows
            ]
            return chunks
        except Exception as e:
            logger.error(f"Error fetching chunks: {e}")
            raise
        finally:
            conn.close()
    
    def soft_delete_document(self, document_id: str) -> None:
        """Mark a document as deleted without removing it."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if document exists
            cursor.execute("SELECT document_id FROM documents WHERE document_id = ?", 
                          (document_id,))
            if not cursor.fetchone():
                raise ValueError(f"Document {document_id} not found")
            
            # Add to deleted_documents table
            cursor.execute("""
                INSERT OR IGNORE INTO deleted_documents (document_id, deleted_at)
                VALUES (?, ?)
            """, (document_id, datetime.utcnow().isoformat() + "Z"))
            
            conn.commit()
            logger.info(f"Soft-deleted document: {document_id}")
        except Exception as e:
            logger.error(f"Error soft-deleting document: {e}")
            raise
        finally:
            conn.close()
    
    def get_deleted_document_ids(self) -> List[str]:
        """Get list of all deleted document IDs."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT document_id FROM deleted_documents")
            rows = cursor.fetchall()
            return [row["document_id"] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching deleted documents: {e}")
            raise
        finally:
            conn.close()
    
    def document_exists(self, document_id: str) -> bool:
        """Check if a document exists and is not deleted."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT d.document_id
                FROM documents d
                LEFT JOIN deleted_documents dd ON d.document_id = dd.document_id
                WHERE d.document_id = ? AND dd.document_id IS NULL
            """, (document_id,))
            
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            raise
        finally:
            conn.close()
