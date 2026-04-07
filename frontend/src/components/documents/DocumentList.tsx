import React from 'react';
import type { Document } from '../../types/index';
import { DocumentCard } from './DocumentCard';
import { FileSignature } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
  isRebuilding: boolean;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, isRebuilding }) => {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <FileSignature className="w-12 h-12 text-gray-400 mb-3 opacity-50" />
        <p className="text-gray-500 text-sm">No documents uploaded yet</p>
        <p className="text-gray-400 text-xs mt-1">Upload a PDF to get started</p>
      </div>
    );
  }

  return (
    <div className="px-4 py-3 space-y-2 max-h-full overflow-y-auto">
      {documents.map((doc) => (
        <DocumentCard key={doc.document_id} document={doc} disabled={isRebuilding} />
      ))}
    </div>
  );
};
