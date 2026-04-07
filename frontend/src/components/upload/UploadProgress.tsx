import React from 'react';

interface UploadProgressProps {
  progress: { percent: number; filename: string };
}

export const UploadProgress: React.FC<UploadProgressProps> = ({ progress }) => {
  return (
    <div className="mt-3">
      <div className="flex justify-between items-center mb-2">
        <p className="text-sm text-gray-300 truncate">{progress.filename}</p>
        <span className="text-xs text-gray-400">{progress.percent}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className="bg-indigo-500 h-full transition-all duration-200"
          style={{ width: `${progress.percent}%` }}
        ></div>
      </div>
    </div>
  );
};
