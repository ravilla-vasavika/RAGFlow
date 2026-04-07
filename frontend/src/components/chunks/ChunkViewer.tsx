import React from 'react';
import type { RetrievedChunk } from '../../types/index';
import { ChunkCard } from './ChunkCard';

interface ChunkViewerProps {
  chunks: RetrievedChunk[];
}

export const ChunkViewer: React.FC<ChunkViewerProps> = ({ chunks }) => {
  return (
    <div className="space-y-2 mt-2">
      {chunks.map((chunk, idx) => (
        <ChunkCard key={`${chunk.document_id}-${chunk.chunk_index}-${idx}`} chunk={chunk} />
      ))}
    </div>
  );
};
