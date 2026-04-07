"""PDF ingestion and text chunking service."""

from typing import List
import pdfplumber
from pathlib import Path
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class IngestionService:
    """Handles PDF parsing and text chunking."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize ingestion service.
        
        Args:
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Extracting text from PDF: {file_path}")
            
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        try:
            logger.info(f"Chunking text into pieces (target size: {self.chunk_size})")
            
            chunks = self.splitter.split_text(text)
            
            logger.info(f"Created {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise
    
    def process_pdf(self, file_path: str) -> List[str]:
        """
        Complete PDF processing pipeline: extract and chunk.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            List of text chunks
        """
        text = self.extract_text_from_pdf(file_path)
        chunks = self.chunk_text(text)
        return chunks
    
    @staticmethod
    def validate_pdf_file(file_path: str, max_size_mb: int = 20) -> None:
        """
        Validate PDF file.
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in megabytes
        
        Raises:
            ValueError: If file is invalid
        """
        # Check extension
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF (.pdf)")
        
        # Check file exists
        if not Path(file_path).exists():
            raise ValueError("File does not exist")
        
        # Check file size
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size ({file_size_mb:.2f} MB) exceeds maximum ({max_size_mb} MB)")
        
        logger.info(f"PDF validation passed: {file_path} ({file_size_mb:.2f} MB)")
