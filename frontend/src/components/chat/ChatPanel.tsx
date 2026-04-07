import React, { useEffect, useRef } from 'react';
import { useChatStore } from '../../store/useChatStore';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

export const ChatPanel: React.FC = () => {
  const { messages, isQuerying } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isQuerying]);

  if (messages.length === 0 && !isQuerying) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <p className="text-lg mb-2">No messages yet</p>
          <p className="text-sm">Select documents and ask a question to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isQuerying && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};
