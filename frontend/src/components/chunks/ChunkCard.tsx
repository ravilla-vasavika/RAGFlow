import React from 'react';
import type { RetrievedChunk } from '../../types/index';

interface ChunkCardProps {
  chunk: RetrievedChunk;
}

const getSimilarityColor = (score: number): string => {
  if (score > 0.7) return 'bg-green-100 text-green-800';
  if (score > 0.5) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};

export const ChunkCard: React.FC<ChunkCardProps> = ({ chunk }) => {
  return (
    <div className="bg-gray-100 border border-gray-300 rounded-lg p-3 text-xs">
      <div className="flex items-center justify-between mb-2 gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-gray-700 font-medium truncate">
            {chunk.filename} (Chunk {chunk.chunk_index})
          </p>
        </div>
        <span className={`badge whitespace-nowrap ${getSimilarityColor(chunk.similarity_score)}`}>
          {(chunk.similarity_score * 100).toFixed(1)}%
        </span>
      </div>
      <pre className="bg-gray-900 text-gray-100 p-2 rounded overflow-x-auto text-xs max-h-48 overflow-y-auto font-mono">
        {chunk.chunk_text}
      </pre>
    </div>
  );
};
