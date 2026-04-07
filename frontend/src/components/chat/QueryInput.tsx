import React, { useState } from 'react';
import { useChatStore } from '../../store/useChatStore';
import { useDocumentStore } from '../../store/useDocumentStore';
import { queryDocuments } from '../../api/query';
import toast from 'react-hot-toast';
import { Send } from 'lucide-react';

export const QueryInput: React.FC = () => {
  const [query, setQuery] = useState('');
  const { addMessage, isQuerying, setQuerying } = useChatStore();
  const { selectedDocumentIds, isRebuilding } = useDocumentStore();

  const canSubmit =
    query.trim().length > 0 &&
    selectedDocumentIds.length > 0 &&
    !isQuerying &&
    !isRebuilding;

  const getDisabledReason = () => {
    if (isRebuilding) return 'Index is rebuilding. Please wait.';
    if (!query.trim()) return 'Enter a query';
    if (selectedDocumentIds.length === 0) return 'Select at least one document';
    if (isQuerying) return 'Query in progress...';
    return '';
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;

    setQuerying(true);
    const userMessage = query.trim();
    const messageId = crypto.randomUUID();

    // Add user message
    addMessage({
      id: messageId,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    });

    setQuery('');

    try {
      const response = await queryDocuments(userMessage, selectedDocumentIds);

      // Add assistant message
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          response.answer ||
          'I could not find relevant information in the selected documents.',
        retrieved_chunks: response.retrieved_chunks,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Query failed';
      toast.error(message);

      // Add error message
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Error: ${message}`,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setQuerying(false);
    }
  };

  const disabledReason = getDisabledReason();

  return (
    <div className="border-t border-gray-200 bg-white p-6">
      <div className="flex gap-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey && canSubmit) {
              handleSubmit();
            }
          }}
          placeholder="Ask a question about your documents..."
          disabled={isRebuilding || isQuerying}
          className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100 resize-none"
          rows={3}
        />

        <div className="flex flex-col justify-end gap-2">
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            title={disabledReason}
            className="btn-primary flex items-center justify-center gap-2 h-12 w-12"
          >
            <Send className="w-5 h-5" />
          </button>
          {!canSubmit && disabledReason && (
            <div className="text-xs text-gray-600 whitespace-nowrap text-right">
              {disabledReason}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
