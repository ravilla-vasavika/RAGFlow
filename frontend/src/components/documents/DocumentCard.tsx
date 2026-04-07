import React, { useState } from 'react';
import type { Document } from '../../types/index';
import { useDocumentStore } from '../../store/useDocumentStore';
import { deleteDocument } from '../../api/documents';
import toast from 'react-hot-toast';
import { Check, Trash2 } from 'lucide-react';

interface DocumentCardProps {
  document: Document;
  disabled: boolean;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ document, disabled }) => {
  const { selectedDocumentIds, toggleDocumentSelection, removeDocument } =
    useDocumentStore();
  const [isDeleting, setIsDeleting] = useState(false);

  const isSelected = selectedDocumentIds.includes(document.document_id);
  const uploadDate = new Date(document.upload_timestamp).toLocaleDateString();

  const handleSelect = () => {
    if (!disabled) {
      toggleDocumentSelection(document.document_id);
    }
  };

  const handleDelete = async () => {
    toast((t) => (
      <div className="flex flex-col gap-2">
        <p className="text-sm">Delete "{document.filename}"?</p>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              toast.dismiss(t.id);
              setIsDeleting(true);
              try {
                await deleteDocument(document.document_id);
                removeDocument(document.document_id);
                toast.success('Document deleted');
              } catch (error) {
                const message =
                  error instanceof Error ? error.message : 'Failed to delete document';
                toast.error(message);
              } finally {
                setIsDeleting(false);
              }
            }}
            disabled={isDeleting}
            className="btn-primary text-xs"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
          <button onClick={() => toast.dismiss(t.id)} className="btn-secondary text-xs">
            Cancel
          </button>
        </div>
      </div>
    ));
  };

  return (
    <div
      onClick={handleSelect}
      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
        isSelected
          ? 'bg-indigo-600 border-2 border-indigo-400'
          : 'bg-gray-800 hover:bg-gray-700 border-2 border-transparent'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div
              className={`w-5 h-5 border-2 rounded flex items-center justify-center flex-shrink-0 ${
                isSelected ? 'bg-white border-white' : 'border-gray-500'
              }`}
            >
              {isSelected && <Check className="w-4 h-4 text-indigo-600" />}
            </div>
            <h4 className="text-sm font-medium text-white truncate">{document.filename}</h4>
          </div>
          <div className="flex items-center gap-2 mt-2 ml-7">
            <span className="text-xs text-gray-400">{uploadDate}</span>
            <span className="badge bg-gray-600 text-white">{document.chunk_count} chunks</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          disabled={disabled}
          className="p-1 hover:bg-red-600 rounded transition-colors flex-shrink-0"
          title="Delete document"
        >
          <Trash2 className="w-4 h-4 text-gray-400 hover:text-white" />
        </button>
      </div>
    </div>
  );
};
