<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Employee Performance Analytics</h1>
            <p class="mt-1 text-sm text-gray-500">K-Means Clustering Analysis Dashboard</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2 text-sm">
              <div class="w-3 h-3 rounded-full" :class="apiStatus ? 'bg-green-400' : 'bg-red-400'"></div>
              <span :class="apiStatus ? 'text-green-600' : 'text-red-600'">
                {{ apiStatus ? 'API Connected' : 'API Disconnected' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Date Range Filter -->
      <div class="mb-8 p-6 bg-white rounded-lg shadow-sm border border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Filter Analysis Period</h2>
        <DateRangePicker
          v-model:date-from="dateFrom"
          v-model:date-to="dateTo"
          :loading="analyticsStore.loading"
          @apply="handleFilterApply"
        />
      </div>

      <!-- Loading State -->
      <div v-if="analyticsStore.loading && !analyticsStore.hasData" class="text-center py-12">
        <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-primary-500 hover:bg-primary-400 transition ease-in-out duration-150 cursor-not-allowed">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading analytics data...
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="analyticsStore.error" class="rounded-md bg-red-50 p-4 mb-8">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error Loading Data</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ analyticsStore.error }}</p>
            </div>
            <div class="mt-4">
              <button @click="handleRetry" class="bg-red-100 px-2 py-1 text-sm font-medium text-red-800 rounded-md hover:bg-red-200">
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div v-else-if="analyticsStore.hasData" class="space-y-8">
        <!-- Overview Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Workers"
            :value="analyticsStore.totalWorkers"
            :icon="UsersIcon"
            color="blue"
            subtitle="Registered employees"
          />
          <StatCard
            title="Active Workers"
            :value="analyticsStore.activeWorkers"
            :icon="UserGroupIcon"
            color="green"
            :subtitle="`${((analyticsStore.activeWorkers / analyticsStore.totalWorkers) * 100).toFixed(1)}% of total`"
          />
          <StatCard
            title="Total Work Hours"
            :value="analyticsStore.overview?.total_work_hours?.toFixed(1) || '0'"
            :icon="ClockIcon"
            color="purple"
            subtitle="Across all workers"
          />
          <StatCard
            title="Model Accuracy"
            :value="`${(analyticsStore.modelAccuracy * 100).toFixed(1)}%`"
            :icon="AcademicCapIcon"
            color="yellow"
            subtitle="Clustering accuracy"
          />
        </div>

        <!-- Clustering Analysis -->
        <div v-if="analyticsStore.clusteringResults" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div class="xl:col-span-1">
            <ClusterChart
              :cluster-data="analyticsStore.clusterDistribution"
              :total-users="analyticsStore.clusteringResults.total_users"
              :accuracy="analyticsStore.modelAccuracy"
            />
          </div>
          
          <div class="xl:col-span-2">
            <div class="card">
              <h3 class="text-lg font-semibold text-gray-900 mb-6">Top Performers</h3>
              <div class="space-y-4">
                <div 
                  v-for="(performer, index) in analyticsStore.topPerformers" 
                  :key="performer.user_id"
                  class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                      <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span class="text-sm font-medium text-primary-600">{{ index + 1 }}</span>
                      </div>
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">{{ performer.name }}</p>
                      <p class="text-sm text-gray-500">{{ performer.worker_id }}</p>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="font-semibold text-gray-900">{{ performer.performance_score.toFixed(1) }}</p>
                    <p class="text-sm text-gray-500">{{ performer.cluster_label }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Table -->
        <PerformanceTable
          v-if="analyticsStore.clusteringResults"
          :employees="analyticsStore.clusteringResults.results"
          title="Detailed Performance Analysis"
        />

        <!-- Trends Chart -->
        <TrendsChart
          v-if="analyticsStore.dailyTrends"
          :trends-data="analyticsStore.dailyTrends"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No data available</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by loading analytics data.</p>
        <div class="mt-6">
          <button @click="handleInitialLoad" class="btn-primary">
            Load Analytics Data
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  UsersIcon, 
  UserGroupIcon, 
  ClockIcon, 
  AcademicCapIcon 
} from '@heroicons/vue/24/outline'

import { useAnalyticsStore } from '@/stores/analytics'
import { apiService } from '@/services/api'

import StatCard from '@/components/StatCard.vue'
import ClusterChart from '@/components/ClusterChart.vue'
import PerformanceTable from '@/components/PerformanceTable.vue'
import TrendsChart from '@/components/TrendsChart.vue'
import DateRangePicker from '@/components/DateRangePicker.vue'

const analyticsStore = useAnalyticsStore()

const apiStatus = ref(false)
const dateFrom = ref('')
const dateTo = ref('')

// Check API status
const checkApiStatus = async () => {
  try {
    await apiService.healthCheck()
    apiStatus.value = true
  } catch (error) {
    apiStatus.value = false
    console.error('API health check failed:', error)
  }
}

const handleInitialLoad = async () => {
  await analyticsStore.fetchAllData()
}

const handleFilterApply = async () => {
  const from = dateFrom.value || undefined
  const to = dateTo.value || undefined
  await analyticsStore.fetchAllData(from, to)
}

const handleRetry = async () => {
  analyticsStore.clearError()
  await handleInitialLoad()
}

onMounted(async () => {
  await checkApiStatus()
  if (apiStatus.value) {
    await handleInitialLoad()
  }
})
</script>