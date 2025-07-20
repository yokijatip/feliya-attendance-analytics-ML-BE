import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data)
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  name: string
  email: string
  role: string
  status: string
  workerId: string
  profileImageUrl?: string
}

export interface AttendanceSummary {
  user_id: string
  total_records: number
  total_work_hours: number
  total_overtime_hours: number
  average_daily_hours: number
  date_range: {
    from: string | null
    to: string | null
  }
}

export interface AnalyticsOverview {
  total_workers: number
  active_workers: number
  total_attendance_records: number
  average_daily_hours: number
  total_work_hours: number
  date_range: {
    from: string | null
    to: string | null
  }
}

export interface ClusteringResult {
  user_id: string
  worker_id: string
  name: string
  cluster: number
  cluster_label: string
  performance_score: number
  features: Record<string, number>
}

export interface ClusteringResponse {
  results: ClusteringResult[]
  cluster_centers: Record<string, number[]>
  feature_names: string[]
  analysis_period: {
    date_from: string
    date_to: string
  }
  total_users: number
  model_accuracy: number
}

export interface TeamPerformance {
  user_id: string
  name: string
  worker_id: string
  email: string
  performance_metrics: {
    total_work_hours: number
    average_daily_hours: number
    attendance_rate: number
    overtime_ratio: number
    punctuality_score: number
    consistency_score: number
    productivity_score: number
  }
}

export interface DailyTrend {
  date: string
  total_hours: number
  total_overtime: number
  unique_workers: number
  average_hours_per_worker: number
}

export interface DailyTrendsResponse {
  daily_trends: DailyTrend[]
  summary: {
    total_days: number
    average_daily_workers: number
    average_daily_hours: number
  }
}

// API Functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Users
  async getUsers(role?: string) {
    const params = role ? { role } : {}
    const response = await api.get('/api/v1/users', { params })
    return response.data as User[]
  },

  async getActiveWorkers() {
    const response = await api.get('/api/v1/users/workers/active')
    return response.data as User[]
  },

  // Analytics
  async getAnalyticsOverview(dateFrom?: string, dateTo?: string) {
    const params: any = {}
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.get('/api/v1/analytics/overview', { params })
    return response.data as AnalyticsOverview
  },

  async getTeamPerformance(dateFrom?: string, dateTo?: string) {
    const params: any = {}
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.get('/api/v1/analytics/team/performance', { params })
    return response.data as TeamPerformance[]
  },

  async getProductivityRanking(dateFrom?: string, dateTo?: string, limit = 10) {
    const params: any = { limit }
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.get('/api/v1/analytics/productivity/ranking', { params })
    return response.data as (TeamPerformance & { rank: number })[]
  },

  async getDailyTrends(dateFrom?: string, dateTo?: string) {
    const params: any = {}
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.get('/api/v1/analytics/trends/daily', { params })
    return response.data as DailyTrendsResponse
  },

  // Machine Learning
  async getQuickClusteringAnalysis(dateFrom?: string, dateTo?: string, nClusters = 3) {
    const params: any = { n_clusters: nClusters }
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.get('/api/v1/ml/clustering/quick-analysis', { params })
    return response.data as ClusteringResponse
  },

  async getMonthlyClusteringAnalysis(year?: number, month?: number, nClusters = 3) {
    const params: any = { n_clusters: nClusters }
    if (year) params.year = year
    if (month) params.month = month
    
    const response = await api.get('/api/v1/ml/clustering/monthly-analysis', { params })
    return response.data as ClusteringResponse
  },

  async getQuarterlyClusteringAnalysis(year?: number, quarter?: number, nClusters = 3) {
    const params: any = { n_clusters: nClusters }
    if (year) params.year = year
    if (quarter) params.quarter = quarter
    
    const response = await api.get('/api/v1/ml/clustering/quarterly-analysis', { params })
    return response.data as ClusteringResponse
  },

  async getYearlyClusteringAnalysis(year?: number, nClusters = 3) {
    const params: any = { n_clusters: nClusters }
    if (year) params.year = year
    
    const response = await api.get('/api/v1/ml/clustering/yearly-analysis', { params })
    return response.data as ClusteringResponse
  },

  async getModelStatus() {
    const response = await api.get('/api/v1/ml/clustering/model-status')
    return response.data
  },

  async retrainModel(dateFrom?: string, dateTo?: string, nClusters = 3) {
    const params: any = { n_clusters: nClusters }
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    
    const response = await api.post('/api/v1/ml/clustering/retrain', null, { params })
    return response.data
  }
}

export default api