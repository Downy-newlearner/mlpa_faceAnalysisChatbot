/**
 * HistorySidebar Component
 * Shows list of previous analyses with ability to load them.
 */

import { useState, useEffect } from 'react';
import './HistorySidebar.css';

export default function HistorySidebar({ 
  analyses = [], 
  currentId = null,
  onSelect,
  onRefresh,
  isLoading = false 
}) {
  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  const getStatusEmoji = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'pending': return '📤';
      case 'failed': return '❌';
      default: return '📋';
    }
  };

  return (
    <aside className="history-sidebar">
      <div className="sidebar-header">
        <h2>📋 분석 기록</h2>
        <button 
          onClick={onRefresh} 
          className="refresh-btn"
          disabled={isLoading}
          title="새로고침"
        >
          🔄
        </button>
      </div>

      <div className="history-list">
        {isLoading && analyses.length === 0 ? (
          <div className="loading-state">
            <div className="spinner-small"></div>
            <span>불러오는 중...</span>
          </div>
        ) : analyses.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📭</span>
            <p>분석 기록이 없습니다</p>
          </div>
        ) : (
          analyses.map((analysis) => (
            <button
              key={analysis.analysis_id}
              className={`history-item ${currentId === analysis.analysis_id ? 'active' : ''}`}
              onClick={() => onSelect(analysis.analysis_id)}
            >
              <div className="item-header">
                <span className="item-status">{getStatusEmoji(analysis.status)}</span>
                <span className="item-date">{formatDate(analysis.created_at)}</span>
              </div>
              <div className="item-info">
                <span className="item-faces">👥 {analysis.total_faces}명</span>
                <span className="item-images">🖼 {analysis.image_count}장</span>
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
