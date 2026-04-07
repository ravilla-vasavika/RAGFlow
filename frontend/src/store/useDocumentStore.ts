import { create } from 'zustand';
import type { Document } from '../types/index';
import { listDocuments, rebuildIndex } from '../api/documents';
import toast from 'react-hot-toast';

interface DocumentStore {
  documents: Document[];
  selectedDocumentIds: string[];
  isUploading: boolean;
  isLoadingDocuments: boolean;
  isRebuilding: boolean;
  toggleDocumentSelection: (id: string) => void;
  addDocument: (doc: Document) => void;
  removeDocument: (id: string) => void;
  fetchDocuments: () => Promise<void>;
  rebuildIndexFromStore: () => Promise<void>;
  setIsUploading: (state: boolean) => void;
  clearSelection: () => void;
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  selectedDocumentIds: [],
  isUploading: false,
  isLoadingDocuments: false,
  isRebuilding: false,

  toggleDocumentSelection: (id: string) => {
    set((state) => {
      const isSelected = state.selectedDocumentIds.includes(id);
      return {
        selectedDocumentIds: isSelected
          ? state.selectedDocumentIds.filter((docId) => docId !== id)
          : [...state.selectedDocumentIds, id],
      };
    });
  },

  addDocument: (doc: Document) => {
    set((state) => {
      // Check if document already exists
      const exists = state.documents.some((d) => d.document_id === doc.document_id);
      if (exists) {
        return state;
      }
      return {
        documents: [doc, ...state.documents],
      };
    });
  },

  removeDocument: (id: string) => {
    set((state) => ({
      documents: state.documents.filter((doc) => doc.document_id !== id),
      selectedDocumentIds: state.selectedDocumentIds.filter((docId) => docId !== id),
    }));
  },

  fetchDocuments: async () => {
    set({ isLoadingDocuments: true });
    try {
      const docs = await listDocuments();
      set({ documents: docs });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load documents';
      toast.error(message);
    } finally {
      set({ isLoadingDocuments: false });
    }
  },

  rebuildIndexFromStore: async () => {
    set({ isRebuilding: true });
    try {
      const result = await rebuildIndex();
      toast.success(
        `Index rebuilt successfully. ${result.chunks_reindexed || 0} chunks reindexed.`
      );
      // Refresh documents after rebuild
      const docs = await listDocuments();
      set({ documents: docs });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to rebuild index';
      toast.error(message);
    } finally {
      set({ isRebuilding: false });
    }
  },

  setIsUploading: (state: boolean) => {
    set({ isUploading: state });
  },

  clearSelection: () => {
    set({ selectedDocumentIds: [] });
  },
}));
