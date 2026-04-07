import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-200 rounded-lg px-4 py-3">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
};
