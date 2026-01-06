/**
 * API client for communicating with the FastAPI backend.
 */

// Use relative path for Vite proxy (avoids CORS issues)
const API_BASE_URL = '/api';

/**
 * Helper to safely parse JSON from a fetch response.
 * Provides better error messages if the response is not valid JSON.
 */
async function getJsonOrText(response) {
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    try {
      return await response.json();
    } catch (e) {
      const text = await response.text();
      throw new Error(`JSON parse error: ${e.message}. Body: ${text.substring(0, 100)}`);
    }
  } else {
    const text = await response.text();
    throw new Error(`Server returned non-JSON response (${response.status}): ${text.substring(0, 100)}`);
  }
}

/**
 * Upload images for analysis.
 * @param {File[]} files - Array of image files to upload
 * @returns {Promise<{analysis_id: string, image_count: number, message: string}>}
 */
export async function uploadImages(files) {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Upload failed (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Start analysis for uploaded images.
 * @param {string} analysisId - The analysis ID from upload
 * @returns {Promise<{analysis_id: string, status: string, message: string}>}
 */
export async function startAnalysis(analysisId) {
  const response = await fetch(`${API_BASE_URL}/analyze/${analysisId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Analysis failed to start (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Get analysis result.
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<{analysis_id: string, status: string, result: object}>}
 */
export async function getResult(analysisId) {
  const response = await fetch(`${API_BASE_URL}/result/${analysisId}`);

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Failed to get result (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Get list of all analyses.
 * @param {number} limit - Maximum number of analyses to return
 * @returns {Promise<{analyses: Array}>}
 */
export async function listAnalyses(limit = 20) {
  const response = await fetch(`${API_BASE_URL}/analyses?limit=${limit}`);

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Failed to get analyses (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Send a chat message about analysis results.
 * @param {string} analysisId - The analysis ID
 * @param {string} question - The user's question
 * @returns {Promise<{analysis_id: string, question: string, answer: string}>}
 */
export async function sendChat(analysisId, question) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      analysis_id: analysisId,
      question: question,
    }),
  });

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Chat failed (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Get chat history for an analysis.
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<{analysis_id: string, history: Array}>}
 */
export async function getChatHistory(analysisId) {
  const response = await fetch(`${API_BASE_URL}/history/${analysisId}`);

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Failed to get history (${response.status})`);
  }

  return getJsonOrText(response);
}

/**
 * Get a natural language summary of analysis results.
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<{analysis_id: string, summary: string, raw_data: object}>}
 */
export async function getSummary(analysisId) {
  const response = await fetch(`${API_BASE_URL}/summary/${analysisId}`);

  if (!response.ok) {
    const error = await getJsonOrText(response);
    throw new Error(error.detail || `Failed to get summary (${response.status})`);
  }

  return getJsonOrText(response);
}
