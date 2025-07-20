<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Daily Performance Trends</h3>
      <div class="flex items-center space-x-2">
        <button 
          @click="chartType = 'hours'"
          :class="chartType === 'hours' ? 'btn-primary' : 'btn-secondary'"
          class="text-sm px-3 py-1"
        >
          Work Hours
        </button>
        <button 
          @click="chartType = 'workers'"
          :class="chartType === 'workers' ? 'btn-primary' : 'btn-secondary'"
          class="text-sm px-3 py-1"
        >
          Active Workers
        </button>
      </div>
    </div>
    
    <div class="relative h-80">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <p class="text-2xl font-bold text-gray-900">{{ summary.total_days }}</p>
        <p class="text-sm text-gray-600">Total Days</p>
      </div>
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <p class="text-2xl font-bold text-gray-900">{{ summary.average_daily_workers.toFixed(1) }}</p>
        <p class="text-sm text-gray-600">Avg Daily Workers</p>
      </div>
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <p class="text-2xl font-bold text-gray-900">{{ summary.average_daily_hours.toFixed(1) }}</p>
        <p class="text-sm text-gray-600">Avg Daily Hours</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { 
  Chart, 
  LineElement, 
  PointElement, 
  LinearScale, 
  CategoryScale, 
  Title, 
  Tooltip, 
  Legend,
  type ChartConfiguration 
} from 'chart.js'
import type { DailyTrendsResponse } from '@/services/api'

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend)

interface Props {
  trendsData: DailyTrendsResponse
}

const props = defineProps<Props>()

const chartCanvas = ref<HTMLCanvasElement>()
const chartType = ref<'hours' | 'workers'>('hours')
let chart: Chart | null = null

const summary = computed(() => props.trendsData.summary)

const createChart = async () => {
  if (!chartCanvas.value || !props.trendsData.daily_trends.length) return
  
  await nextTick()
  
  if (chart) {
    chart.destroy()
  }
  
  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return
  
  const labels = props.trendsData.daily_trends.map(trend => {
    const date = new Date(trend.date)
    return date.toLocaleDateString('id-ID', { month: 'short', day: 'numeric' })
  })
  
  const data = chartType.value === 'hours' 
    ? props.trendsData.daily_trends.map(trend => trend.total_hours)
    : props.trendsData.daily_trends.map(trend => trend.unique_workers)
  
  const config: ChartConfiguration = {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: chartType.value === 'hours' ? 'Total Work Hours' : 'Active Workers',
        data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: (context) => {
              const value = context.parsed.y
              const suffix = chartType.value === 'hours' ? ' hours' : ' workers'
              return `${context.dataset.label}: ${value.toFixed(1)}${suffix}`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false
          }
        },
        y: {
          display: true,
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  }
  
  chart = new Chart(ctx, config)
}

onMounted(() => {
  createChart()
})

watch(() => props.trendsData, () => {
  createChart()
}, { deep: true })

watch(chartType, () => {
  createChart()
})
</script>