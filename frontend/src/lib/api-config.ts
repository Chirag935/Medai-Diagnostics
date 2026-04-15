// API Configuration - Updated Render URL
export const API_BASE_URL = 'https://medai-backend-v0hl.onrender.com'

// API Endpoints
export const API_ENDPOINTS = {
  pneumonia: `${API_BASE_URL}/api/pneumonia`,
  malaria: `${API_BASE_URL}/api/malaria`,
  diabetes: `${API_BASE_URL}/api/diabetes`,
  breastCancer: `${API_BASE_URL}/api/breast-cancer`,
  heartDisease: `${API_BASE_URL}/api/heart-disease`,
  kidneyDisease: `${API_BASE_URL}/api/kidney-disease`,
  liverDisease: `${API_BASE_URL}/api/liver-disease`,
  alzheimer: `${API_BASE_URL}/api/alzheimer`,
  metrics: `${API_BASE_URL}/api/metrics`,
}

// Helper function for API calls
export async function apiFetch(endpoint: string, options?: RequestInit) {
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }
  
  return response.json()
}
