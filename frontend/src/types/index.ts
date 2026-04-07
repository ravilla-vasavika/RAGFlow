export interface Document {
  document_id: string;
  filename: string;
  upload_timestamp: string;
  chunk_count: number;
}

export interface RetrievedChunk {
  document_id: string;
  filename: string;
  chunk_index: number;
  chunk_text: string;
  similarity_score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  retrieved_chunks?: RetrievedChunk[];
  timestamp: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  chunks_created: number;
  message: string;
}

export interface ListDocumentsResponse {
  documents: Document[];
}

export interface QueryResponse {
  answer: string;
  retrieved_chunks: RetrievedChunk[];
}

export interface DeleteResponse {
  message: string;
  document_id?: string;
}

export interface RebuildIndexResponse {
  message: string;
  chunks_reindexed?: number;
}

export interface ApiError {
  detail?: string;
  message?: string;
}
