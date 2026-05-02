import React, { useState, useRef } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import axios from 'axios';

const ResumeUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setError('');
    if (selectedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file.');
      return;
    }
    setFile(selectedFile);
  };

  const handleSubmit = async () => {
    if (!file) return;

    setIsLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post('http://localhost:5000/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      onUploadSuccess({
        resumeText: response.data.resumeText,
        initialMessage: response.data.initialMessage
      });
    } catch (err) {
      console.error(err);
      setError('Failed to process resume. Please ensure the backend is running and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <div 
        className={`upload-area ${isDragging ? 'drag-active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileInput} 
          accept=".pdf" 
          style={{ display: 'none' }} 
        />
        
        {file ? (
          <div>
            <FileText className="upload-icon" size={48} />
            <div className="upload-text">{file.name}</div>
            <div className="upload-hint">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
          </div>
        ) : (
          <div>
            <UploadCloud className="upload-icon" size={48} />
            <div className="upload-text">Drag & Drop your Resume</div>
            <div className="upload-hint">or click to browse (PDF only)</div>
          </div>
        )}
      </div>

      {error && (
        <div style={{ color: 'var(--error)', marginTop: '1rem', textAlign: 'center' }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <button 
          className="btn" 
          onClick={handleSubmit} 
          disabled={!file || isLoading}
          style={{ width: '100%', maxWidth: '300px' }}
        >
          {isLoading ? (
            <>
              <div className="spinner"></div>
              Analyzing Resume...
            </>
          ) : (
            'Start Interview'
          )}
        </button>
      </div>
    </div>
  );
};

export default ResumeUpload;
