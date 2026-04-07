import axiosInstance from './axiosInstance';
import type {
  Document,
  UploadResponse,
  ListDocumentsResponse,
  DeleteResponse,
  RebuildIndexResponse,
} from '../types/index';

export const uploadPdf = async (
  file: File,
  onProgress: (percent: number) => void
): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axiosInstance.post<UploadResponse>('/api/upload_pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });

  return {
    document_id: response.data.document_id,
    filename: response.data.filename,
    upload_timestamp: new Date().toISOString(),
    chunk_count: response.data.chunks_created,
  };
};

export const listDocuments = async (): Promise<Document[]> => {
  const response = await axiosInstance.get<ListDocumentsResponse>('/api/list_documents');
  return response.data.documents;
};

export const deleteDocument = async (id: string): Promise<string> => {
  const response = await axiosInstance.delete<DeleteResponse>(`/api/document/${id}`);
  return response.data.message;
};

export const rebuildIndex = async (): Promise<RebuildIndexResponse> => {
  const response = await axiosInstance.post<RebuildIndexResponse>('/api/rebuild_index');
  return response.data;
};
