/**
 * ImageUploader Component
 * Handles drag-and-drop and click-to-upload image functionality.
 */

import { useState, useCallback } from 'react';
import './ImageUploader.css';

export default function ImageUploader({ onUpload, isUploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const processFiles = useCallback((files) => {
    const imageFiles = Array.from(files).filter(file => 
      file.type.startsWith('image/')
    );
    
    setSelectedFiles(imageFiles);
    
    // Create previews
    const newPreviews = imageFiles.map(file => ({
      name: file.name,
      url: URL.createObjectURL(file)
    }));
    setPreviews(prev => {
      // Cleanup old URLs
      prev.forEach(p => URL.revokeObjectURL(p.url));
      return newPreviews;
    });
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleChange = useCallback((e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  }, [processFiles]);

  const handleUpload = useCallback(() => {
    if (selectedFiles.length > 0 && onUpload) {
      onUpload(selectedFiles);
    }
  }, [selectedFiles, onUpload]);

  const clearFiles = useCallback(() => {
    previews.forEach(p => URL.revokeObjectURL(p.url));
    setSelectedFiles([]);
    setPreviews([]);
  }, [previews]);

  return (
    <div className="uploader-container">
      <div 
        className={`dropzone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          multiple
          accept="image/*"
          onChange={handleChange}
          className="file-input"
        />
        <label htmlFor="file-input" className="dropzone-label">
          <div className="upload-icon">📷</div>
          <p className="upload-text">
            이미지를 드래그하거나 클릭하여 업로드
          </p>
          <p className="upload-hint">
            JPG, PNG, BMP, WebP 지원 (여러 장 가능)
          </p>
        </label>
      </div>

      {previews.length > 0 && (
        <div className="preview-section">
          <div className="preview-header">
            <span>{previews.length}개 이미지 선택됨</span>
            <button onClick={clearFiles} className="clear-btn">초기화</button>
          </div>
          <div className="preview-grid">
            {previews.map((preview, index) => (
              <div key={index} className="preview-item">
                <img src={preview.url} alt={preview.name} />
                <span className="preview-name">{preview.name}</span>
              </div>
            ))}
          </div>
          <button 
            onClick={handleUpload} 
            disabled={isUploading}
            className="upload-btn"
          >
            {isUploading ? '업로드 중...' : '분석 시작'}
          </button>
        </div>
      )}
    </div>
  );
}
