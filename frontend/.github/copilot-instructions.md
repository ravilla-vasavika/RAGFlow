# RAGFlow Frontend - Coding Guidelines

## Project Overview
Production-grade React 18 + Vite frontend for RAGFlow, a Retrieval-Augmented Generation application.

## Tech Stack
- React 18 with TypeScript (strict mode)
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- Axios for API calls
- react-hot-toast for notifications
- react-dropzone for file uploads

## Core Principles
1. **Strict TypeScript**: No `any` types anywhere. All props, state, and API responses must be fully typed.
2. **Interfaces First**: Define all types in `/src/types/index.ts` and reuse globally.
3. **Component Isolation**: Each component handles its own loading, error, and empty states.
4. **Zustand Stores**: Centralized state management for documents and chat messages.
5. **API Layer Abstraction**: Type-safe API functions in `/src/api/` with shared axios instance.
6. **Tailwind Only**: No inline styles—use utility classes exclusively.
7. **Toast Notifications**: All user feedback via react-hot-toast, no alert() calls.
8. **Responsive Design**: Mobile-first approach with sidebar collapse on small screens.

## File Structure
```
/src
  /components
    /upload        → DropZone, UploadProgress, UploadStatus
    /documents     → DocumentList, DocumentCard
    /chat          → ChatPanel, MessageBubble, QueryInput, TypingIndicator
    /chunks        → ChunkViewer, ChunkCard
    /layout        → Sidebar, MainPanel, Header
  /store           → useDocumentStore, useChatStore
  /api             → axiosInstance, documents, query
  /types           → TypeScript interfaces (no any types)
  App.tsx
  main.tsx
```

## API Contract
- Backend: `http://localhost:8000`
- Endpoints: `/api/upload_pdf`, `/api/list_documents`, `/api/query`, `/api/document/:id`, `/api/rebuild_index`
- Response bodies always include error detail field when applicable

## Key Components Features
1. **PDF Upload**: Drag-drop validation, progress bar, error handling
2. **Document Management**: Selection state, delete with confirmation, empty state
3. **Chat Interface**: Message history with typing indicator, source chunk viewer
4. **Index Management**: Rebuild button with confirmation and progress indicator
5. **isRebuilding Guard**: All interactive elements disabled during rebuild

## Styling Conventions
- Dark sidebar: `bg-gray-900` text-white
- Light main: `bg-gray-50` text-gray-900
- Primary accent: `indigo-500` / `indigo-600`
- Font: Inter from Google Fonts
- Cards: `rounded-xl shadow-sm`
- Transitions: `transition-all duration-200`

## Development Commands
- `npm run dev` – Start Vite dev server
- `npm run build` – Production build
- `npm run preview` – Preview production build
- `npm run lint` – Type checking and linting

## Important Notes
- Message IDs generated with `crypto.randomUUID()`
- Always check `isRebuilding` state before enabling interactive elements
- API errors must extract `detail` field from response body
- Responsive sidebar collapses to drawer on mobile with hamburger menu
