import React from 'react';
import { useDocumentStore } from '../../store/useDocumentStore';
import { useChatStore } from '../../store/useChatStore';
import toast from 'react-hot-toast';

export const Header: React.FC = () => {
  const { isRebuilding, rebuildIndexFromStore, clearSelection } = useDocumentStore();
  const { clearChat } = useChatStore();

  const handleRebuildClick = () => {
    toast((t) => (
      <div className="flex flex-col gap-3">
        <p>This will rebuild the FAISS index from the database. Continue?</p>
        <div className="flex gap-2">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              rebuildIndexFromStore();
            }}
            className="btn-primary text-sm"
          >
            Continue
          </button>
          <button onClick={() => toast.dismiss(t.id)} className="btn-secondary text-sm">
            Cancel
          </button>
        </div>
      </div>
    ));
  };

  const handleClearChat = () => {
    clearChat();
    clearSelection();
    toast.success('Chat cleared');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h1 className="text-2xl font-bold text-gray-900">RAGFlow</h1>

      {isRebuilding && (
        <div className="absolute inset-0 bg-yellow-50 border-b border-yellow-200 px-6 py-3 text-sm text-yellow-800 flex items-center gap-2">
          <div className="animate-spin w-4 h-4 border border-yellow-600 border-t-transparent rounded-full"></div>
          Index rebuild in progress. Please wait before uploading or querying.
        </div>
      )}

      <div className="flex items-center gap-3">
        <button
          onClick={handleClearChat}
          disabled={isRebuilding}
          className="btn-secondary"
        >
          Clear Chat
        </button>
        <button
          onClick={handleRebuildClick}
          disabled={isRebuilding}
          className="btn-primary relative"
        >
          {isRebuilding ? (
            <>
              <div className="animate-spin w-4 h-4 border border-white border-t-transparent rounded-full mr-2 inline-block"></div>
              Rebuilding...
            </>
          ) : (
            'Rebuild Index'
          )}
        </button>
      </div>
    </header>
  );
};
