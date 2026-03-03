import axios, { AxiosRequestConfig, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper to get token from localStorage
const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token')
  }
  return null
}

const getRefreshToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('refresh_token')
  }
  return null
}

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to every request
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    console.log('[API Interceptor] URL:', config.url, 'Token exists:', !!token)
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
      console.log('[API Interceptor] Added Authorization header')
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle 401 errors with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = getRefreshToken()
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token: newRefreshToken } = response.data
          localStorage.setItem('token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data: { name: string; email: string; password: string }) =>
    api.post('/auth/register', data),

  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getMe: () => api.get('/auth/me'),
}

// Resume API
export const resumeApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  list: () => api.get('/resume/'),

  get: (id: number) => api.get(`/resume/${id}`),

  delete: (id: number) => api.delete(`/resume/${id}`),

  checkFormat: (id: number) => api.get(`/resume/${id}/format-check`),
}

// Jobs API
export const jobsApi = {
  create: (data: { title: string; description: string }) =>
    api.post('/jobs/', data),

  list: () => api.get('/jobs/'),

  get: (id: number) => api.get(`/jobs/${id}`),

  update: (id: number, data: { title: string; description: string }) =>
    api.put(`/jobs/${id}`, data),

  delete: (id: number) => api.delete(`/jobs/${id}`),
}

// Score API
export const scoreApi = {
  calculate: (resumeId: number, jobId: number) =>
    api.post('/score/calculate', { resume_id: resumeId, job_id: jobId }),

  history: (resumeId?: number, jobId?: number) =>
    api.get('/score/history', { params: { resume_id: resumeId, job_id: jobId } }),

  get: (id: number) => api.get(`/score/${id}`),

  delete: (id: number) => api.delete(`/score/${id}`),
}

// History & Dashboard API
export const historyApi = {
  getHistory: (params?: { page?: number; per_page?: number; sort_by?: string; grade_filter?: string }) =>
    api.get('/resume/history', { params }),
  
  deleteAnalysis: (scoreId: number) =>
    api.delete(`/resume/history/${scoreId}`),
  
  getDashboardStats: () =>
    api.get('/resume/dashboard-stats'),
}

// Types for history
export interface HistoryItem {
  id: number
  file_name: string
  total_score: number
  grade: string
  summary: string | null
  created_at: string
  is_standalone: boolean
}

export interface HistoryResponse {
  items: HistoryItem[]
  total: number
  page: number
  per_page: number
}

export interface DashboardStats {
  resumes_analyzed: number
  average_score: number
  optimized_resumes: number
  issues_fixed: number
  score_distribution: Record<string, number>
  recent_trend: Array<{ date: string; score: number; count: number }>
}

export default api
