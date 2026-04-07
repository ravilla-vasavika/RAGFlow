import React, { useEffect } from 'react';
import { useDocumentStore } from '../../store/useDocumentStore';
import { DropZone } from '../upload/DropZone';
import { DocumentList } from '../documents/DocumentList';
import { FileText } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { documents, selectedDocumentIds, isLoadingDocuments, isRebuilding, fetchDocuments } =
    useDocumentStore();

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const selectedCount = selectedDocumentIds.length;

  return (
    <aside className="w-80 bg-gray-900 text-white flex flex-col border-r border-gray-700">
      {/* Sidebar Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-6 h-6 text-indigo-400" />
          <h2 className="text-2xl font-bold">RAGFlow</h2>
        </div>

        {/* Selection Badge */}
        {selectedCount > 0 && (
          <div className="badge mb-4 bg-indigo-600 text-white">
            {selectedCount} document{selectedCount !== 1 ? 's' : ''} selected
          </div>
        )}
      </div>

      {/* Upload Section */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase">Upload PDF</h3>
        <DropZone />
      </div>

      {/* Documents Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 uppercase">
            Documents ({documents.length})
          </h3>
        </div>

        {isLoadingDocuments ? (
          <div className="p-6 text-center text-gray-400">Loading documents...</div>
        ) : (
          <DocumentList documents={documents} isRebuilding={isRebuilding} />
        )}
      </div>
    </aside>
  );
};
