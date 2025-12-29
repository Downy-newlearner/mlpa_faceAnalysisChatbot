/**
 * ChatInterface Component
 * ChatGPT-style chat interface for asking questions about analysis results.
 */

import { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

export default function ChatInterface({ 
  analysisId, 
  onSendMessage, 
  messages = [], 
  isLoading = false,
  disabled = false 
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading && !disabled && onSendMessage) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const suggestedQuestions = [
    "남녀 비율은 어떻게 되나요?",
    "20대가 몇 명인가요?",
    "가장 많은 연령대는?",
    "분석 결과를 요약해주세요",
  ];

  return (
    <div className="chat-container">
      <div className="chat-header">
        <span className="chat-icon">💬</span>
        <h3>분석 결과 질문하기</h3>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="welcome-icon">🤖</div>
            <p className="welcome-text">
              안녕하세요! 이미지 분석 결과에 대해 질문해 주세요.
            </p>
            <div className="suggested-questions">
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  className="suggested-btn"
                  onClick={() => {
                    if (!disabled && onSendMessage) {
                      onSendMessage(q);
                    }
                  }}
                  disabled={disabled || isLoading}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`chat-message ${msg.role}`}
          >
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <p>{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "분석 완료 후 질문할 수 있습니다" : "질문을 입력하세요..."}
          disabled={disabled || isLoading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={!input.trim() || isLoading || disabled}
          className="send-btn"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" />
          </svg>
        </button>
      </form>
    </div>
  );
}
