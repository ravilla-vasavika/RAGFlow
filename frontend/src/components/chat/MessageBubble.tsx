import React, { useState } from 'react';
import type { Message } from '../../types/index';
import { ChunkViewer } from '../chunks/ChunkViewer';
import { ChevronDown } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === 'user';
  const hasChunks = message.retrieved_chunks && message.retrieved_chunks.length > 0;

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-2xl">
          <div className="bg-indigo-600 text-white rounded-lg px-4 py-3">
            <p className="text-sm">{message.content}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-2xl">
        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
          <p className="text-sm text-gray-900">{message.content}</p>

          {hasChunks && (
            <button
              onClick={() => setShowSources(!showSources)}
              className="mt-3 text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
            >
              <ChevronDown
                className={`w-4 h-4 transition-transform ${showSources ? 'rotate-180' : ''}`}
              />
              View Sources ({message.retrieved_chunks!.length})
            </button>
          )}
        </div>

        {showSources && hasChunks && (
          <div className="mt-2 animate-in fade-in slide-in-from-top-2 duration-200">
            <ChunkViewer chunks={message.retrieved_chunks!} />
          </div>
        )}
      </div>
    </div>
  );
};
