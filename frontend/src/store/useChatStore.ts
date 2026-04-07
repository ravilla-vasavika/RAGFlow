import { create } from 'zustand';
import type { Message } from '../types/index';

interface ChatStore {
  messages: Message[];
  isQuerying: boolean;
  addMessage: (message: Message) => void;
  setQuerying: (state: boolean) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isQuerying: false,

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  setQuerying: (state: boolean) => {
    set({ isQuerying: state });
  },

  clearChat: () => {
    set({ messages: [] });
  },
}));
