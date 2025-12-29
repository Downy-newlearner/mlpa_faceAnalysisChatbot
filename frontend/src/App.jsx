/**
 * Face Detection Chatbot - Main Application
 * Integrates image upload, analysis, chat, and history functionality.
 */

import { useState, useCallback, useEffect } from 'react';
import ImageUploader from './components/ImageUploader';
import AnalysisResult from './components/AnalysisResult';
import ChatInterface from './components/ChatInterface';
import HistorySidebar from './components/HistorySidebar';
import { uploadImages, startAnalysis, getResult, sendChat, listAnalyses, getChatHistory } from './api/client';
import logo from './assets/logo.png';
import './App.css';

function App() {
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // History state
  const [analyses, setAnalyses] = useState([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const data = await listAnalyses(20);
      setAnalyses(data.analyses || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  // Poll for analysis result when processing
  useEffect(() => {
    let pollInterval;
    
    if (analysisId && status === 'processing') {
      pollInterval = setInterval(async () => {
        try {
          const data = await getResult(analysisId);
          setStatus(data.status);
          
          if (data.status === 'completed' && data.result) {
            setResult(data.result);
            clearInterval(pollInterval);
            loadHistory(); // Refresh history
          } else if (data.status === 'failed') {
            clearInterval(pollInterval);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 2000);
    }
    
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [analysisId, status]);

  const handleUpload = useCallback(async (files) => {
    setIsUploading(true);
    setError(null);
    
    try {
      const uploadData = await uploadImages(files);
      setAnalysisId(uploadData.analysis_id);
      setStatus('pending');
      setResult(null);
      setMessages([]);
      
      const analyzeData = await startAnalysis(uploadData.analysis_id);
      setStatus(analyzeData.status);
      loadHistory();
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleSelectAnalysis = useCallback(async (id) => {
    if (id === analysisId) return;
    
    setAnalysisId(id);
    setMessages([]);
    setError(null);
    
    try {
      // Load result
      const data = await getResult(id);
      setStatus(data.status);
      setResult(data.result);
      
      // Load chat history
      if (data.status === 'completed') {
        try {
          const historyData = await getChatHistory(id);
          const loadedMessages = historyData.history.map(h => ([
            { role: 'user', content: h.question },
            { role: 'assistant', content: h.answer }
          ])).flat();
          setMessages(loadedMessages);
        } catch (e) {
          // No history, that's ok
        }
      }
    } catch (err) {
      setError(err.message);
    }
  }, [analysisId]);

  const handleSendMessage = useCallback(async (question) => {
    if (!analysisId || status !== 'completed') return;
    
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setIsChatLoading(true);
    
    try {
      const data = await sendChat(analysisId, question);
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `오류가 발생했습니다: ${err.message}` 
      }]);
    } finally {
      setIsChatLoading(false);
    }
  }, [analysisId, status]);

  const handleNewAnalysis = useCallback(() => {
    setAnalysisId(null);
    setStatus(null);
    setResult(null);
    setMessages([]);
    setError(null);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <img src={logo} alt="MLPA Logo" className="header-logo" />
            Face Detection Chatbot
          </h1>
          <p className="subtitle">
            이미지에서 얼굴을 감지하고, 성별과 연령대를 분석합니다
          </p>
        </div>
        <button onClick={handleNewAnalysis} className="new-analysis-btn">
          + 새 분석
        </button>
      </header>

      <div className="app-body">
        <HistorySidebar
          analyses={analyses}
          currentId={analysisId}
          onSelect={handleSelectAnalysis}
          onRefresh={loadHistory}
          isLoading={isHistoryLoading}
        />

        <main className="app-main">
          {error && (
            <div className="error-banner">
              <span>⚠️</span>
              <p>{error}</p>
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {!analysisId ? (
            <section className="upload-section">
              <ImageUploader 
                onUpload={handleUpload} 
                isUploading={isUploading} 
              />
            </section>
          ) : (
            <div className="analysis-layout">
              <section className="result-section">
                <AnalysisResult 
                  result={result} 
                  status={status} 
                />
              </section>
              
              <section className="chat-section">
                <ChatInterface
                  analysisId={analysisId}
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  isLoading={isChatLoading}
                  disabled={status !== 'completed'}
                />
              </section>
            </div>
          )}
        </main>
      </div>

      <footer className="app-footer">
        <p>MLPA Face Detection Chatbot © 2025</p>
        <p className="footer-author">Made by Dahun Chung (jdh251425142514@gmail.com)</p>
      </footer>
    </div>
  );
}

export default App;
