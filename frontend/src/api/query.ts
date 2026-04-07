import axiosInstance from './axiosInstance';
import type { QueryResponse } from '../types/index';

export const queryDocuments = async (
  query: string,
  document_ids: string[],
  top_k: number = 5
): Promise<QueryResponse> => {
  const response = await axiosInstance.post<QueryResponse>('/api/query', {
    query,
    document_ids,
    top_k,
  });

  return response.data;
};
