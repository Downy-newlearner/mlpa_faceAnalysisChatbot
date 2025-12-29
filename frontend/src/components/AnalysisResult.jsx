/**
 * AnalysisResult Component
 * Displays analysis results with statistics and charts.
 */

import './AnalysisResult.css';

export default function AnalysisResult({ result, status }) {
  if (status === 'pending') {
    return (
      <div className="result-container">
        <div className="status-badge pending">대기 중</div>
        <p className="status-message">이미지가 업로드되었습니다. 분석을 시작하세요.</p>
      </div>
    );
  }

  if (status === 'processing') {
    return (
      <div className="result-container">
        <div className="status-badge processing">분석 중</div>
        <div className="loading-spinner"></div>
        <p className="status-message">이미지를 분석하고 있습니다...</p>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="result-container">
        <div className="status-badge failed">실패</div>
        <p className="status-message">분석 중 오류가 발생했습니다.</p>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const { total_faces, gender, age_group } = result;
  const malePercent = total_faces > 0 ? ((gender.male / total_faces) * 100).toFixed(1) : 0;
  const femalePercent = total_faces > 0 ? ((gender.female / total_faces) * 100).toFixed(1) : 0;

  return (
    <div className="result-container">
      <div className="status-badge completed">분석 완료</div>
      
      <div className="stat-card total">
        <div className="stat-icon">👥</div>
        <div className="stat-info">
          <span className="stat-value">{total_faces}</span>
          <span className="stat-label">감지된 얼굴</span>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card gender">
          <h3>성별 분포</h3>
          <div className="gender-bars">
            <div className="gender-bar-container">
              <div className="gender-label">
                <span>👨 남성</span>
                <span>{gender.male}명 ({malePercent}%)</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill male" 
                  style={{ width: `${malePercent}%` }}
                ></div>
              </div>
            </div>
            <div className="gender-bar-container">
              <div className="gender-label">
                <span>👩 여성</span>
                <span>{gender.female}명 ({femalePercent}%)</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill female" 
                  style={{ width: `${femalePercent}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="stat-card age">
          <h3>연령대 분포</h3>
          <div className="age-grid">
            {[
              { key: '10s', label: '10대', emoji: '🧒' },
              { key: '20s', label: '20대', emoji: '🧑' },
              { key: '30s', label: '30대', emoji: '👨' },
              { key: '40_plus', label: '40대+', emoji: '👴' },
            ].map(({ key, label, emoji }) => (
              <div key={key} className="age-item">
                <span className="age-emoji">{emoji}</span>
                <span className="age-value">{age_group[key] || 0}</span>
                <span className="age-label">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
