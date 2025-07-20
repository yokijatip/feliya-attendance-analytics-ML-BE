import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService, type AnalyticsOverview, type TeamPerformance, type ClusteringResponse, type DailyTrendsResponse } from '@/services/api'

export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Analytics data
  const overview = ref<AnalyticsOverview | null>(null)
  const teamPerformance = ref<TeamPerformance[]>([])
  const clusteringResults = ref<ClusteringResponse | null>(null)
  const dailyTrends = ref<DailyTrendsResponse | null>(null)
  const productivityRanking = ref<(TeamPerformance & { rank: number })[]>([])
  
  // Date filters
  const dateFrom = ref<string>('')
  const dateTo = ref<string>('')
  
  // Computed
  const hasData = computed(() => overview.value !== null)
  const totalWorkers = computed(() => overview.value?.total_workers || 0)
  const activeWorkers = computed(() => overview.value?.active_workers || 0)
  const modelAccuracy = computed(() => clusteringResults.value?.model_accuracy || 0)
  
  // Cluster distribution
  const clusterDistribution = computed(() => {
    if (!clusteringResults.value) return []
    
    const distribution: Record<string, number> = {}
    clusteringResults.value.results.forEach(result => {
      distribution[result.cluster_label] = (distribution[result.cluster_label] || 0) + 1
    })
    
    return Object.entries(distribution).map(([label, count]) => ({
      label,
      count,
      percentage: (count / clusteringResults.value!.total_users) * 100
    }))
  })
  
  // Top performers
  const topPerformers = computed(() => {
    if (!clusteringResults.value) return []
    
    return [...clusteringResults.value.results]
      .sort((a, b) => b.performance_score - a.performance_score)
      .slice(0, 5)
  })
  
  // Actions
  async function fetchOverview(from?: string, to?: string) {
    try {
      loading.value = true
      error.value = null
      
      overview.value = await apiService.getAnalyticsOverview(from, to)
    } catch (err) {
      error.value = 'Failed to fetch analytics overview'
      console.error('Error fetching overview:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchTeamPerformance(from?: string, to?: string) {
    try {
      loading.value = true
      error.value = null
      
      teamPerformance.value = await apiService.getTeamPerformance(from, to)
    } catch (err) {
      error.value = 'Failed to fetch team performance'
      console.error('Error fetching team performance:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchClusteringAnalysis(from?: string, to?: string, clusters = 3) {
    try {
      loading.value = true
      error.value = null
      
      clusteringResults.value = await apiService.getQuickClusteringAnalysis(from, to, clusters)
    } catch (err) {
      error.value = 'Failed to fetch clustering analysis'
      console.error('Error fetching clustering:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchDailyTrends(from?: string, to?: string) {
    try {
      loading.value = true
      error.value = null
      
      dailyTrends.value = await apiService.getDailyTrends(from, to)
    } catch (err) {
      error.value = 'Failed to fetch daily trends'
      console.error('Error fetching daily trends:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchProductivityRanking(from?: string, to?: string, limit = 10) {
    try {
      loading.value = true
      error.value = null
      
      productivityRanking.value = await apiService.getProductivityRanking(from, to, limit)
    } catch (err) {
      error.value = 'Failed to fetch productivity ranking'
      console.error('Error fetching productivity ranking:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchAllData(from?: string, to?: string) {
    dateFrom.value = from || ''
    dateTo.value = to || ''
    
    await Promise.all([
      fetchOverview(from, to),
      fetchTeamPerformance(from, to),
      fetchClusteringAnalysis(from, to),
      fetchDailyTrends(from, to),
      fetchProductivityRanking(from, to)
    ])
  }
  
  function setDateRange(from: string, to: string) {
    dateFrom.value = from
    dateTo.value = to
  }
  
  function clearError() {
    error.value = null
  }
  
  return {
    // State
    loading,
    error,
    overview,
    teamPerformance,
    clusteringResults,
    dailyTrends,
    productivityRanking,
    dateFrom,
    dateTo,
    
    // Computed
    hasData,
    totalWorkers,
    activeWorkers,
    modelAccuracy,
    clusterDistribution,
    topPerformers,
    
    // Actions
    fetchOverview,
    fetchTeamPerformance,
    fetchClusteringAnalysis,
    fetchDailyTrends,
    fetchProductivityRanking,
    fetchAllData,
    setDateRange,
    clearError
  }
})