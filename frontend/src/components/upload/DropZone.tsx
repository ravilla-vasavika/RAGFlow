import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useDocumentStore } from '../../store/useDocumentStore';
import { uploadPdf } from '../../api/documents';
import toast from 'react-hot-toast';
import { Upload } from 'lucide-react';
import { UploadProgress } from './UploadProgress';

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

export const DropZone: React.FC = () => {
  const { addDocument, isRebuilding, setIsUploading } = useDocumentStore();
  const [uploadProgress, setUploadProgress] = useState<{ percent: number; filename: string } | null>(
    null
  );
  const [validationError, setValidationError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[], rejectedFiles: any[]) => {
      setValidationError(null);

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === 'file-invalid-type') {
          setValidationError('Only PDF files are accepted');
          return;
        }
        if (rejection.errors[0]?.code === 'file-too-large') {
          setValidationError('File size must be less than 20MB');
          return;
        }
      }

      if (acceptedFiles.length === 0) {
        return;
      }

      const file = acceptedFiles[0];

      // Client-side validation
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setValidationError('Only PDF files are accepted');
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        setValidationError('File size must be less than 20MB');
        return;
      }

      // Upload
      setIsUploading(true);
      setUploadProgress({ percent: 0, filename: file.name });

      try {
        const doc = await uploadPdf(file, (percent) => {
          setUploadProgress((prev) => (prev ? { ...prev, percent } : null));
        });

        addDocument(doc);
        toast.success(`"${file.name}" uploaded successfully`);
        setUploadProgress(null);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Upload failed';
        toast.error(message);
        setUploadProgress(null);
      } finally {
        setIsUploading(false);
      }
    },
    [addDocument, isRebuilding, setIsUploading]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: MAX_FILE_SIZE,
    disabled: isRebuilding,
    multiple: false,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-indigo-400 bg-indigo-900 bg-opacity-20'
            : 'border-gray-600 hover:border-gray-500 hover:bg-gray-800 bg-gray-800 bg-opacity-50'
        } ${isRebuilding ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />

        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-300">
          {isDragActive ? 'Drop the PDF here...' : 'Drag & drop a PDF or click to select'}
        </p>
        <p className="text-xs text-gray-500 mt-1">Max 20MB</p>
      </div>

      {validationError && (
        <div className="mt-3 p-3 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg">
          <p className="text-sm text-red-300">{validationError}</p>
        </div>
      )}

      {uploadProgress && <UploadProgress progress={uploadProgress} />}
    </div>
  );
};
