import React from 'react';
import { ChatPanel } from '../chat/ChatPanel';
import { QueryInput } from '../chat/QueryInput';

export const MainPanel: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      <ChatPanel />
      <QueryInput />
    </div>
  );
};
