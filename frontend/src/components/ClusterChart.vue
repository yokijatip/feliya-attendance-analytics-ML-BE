<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Performance Clusters</h3>
      <div class="flex items-center space-x-2 text-sm text-gray-500">
        <span>Accuracy:</span>
        <span class="font-medium text-gray-900">{{ (accuracy * 100).toFixed(1) }}%</span>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Pie Chart -->
      <div class="relative">
        <canvas ref="chartCanvas" width="300" height="300"></canvas>
      </div>
      
      <!-- Legend and Stats -->
      <div class="space-y-4">
        <div v-for="(cluster, index) in clusterData" :key="cluster.label" class="flex items-center justify-between p-3 rounded-lg border">
          <div class="flex items-center space-x-3">
            <div 
              class="w-4 h-4 rounded-full" 
              :style="{ backgroundColor: getClusterColor(index) }"
            ></div>
            <div>
              <p class="font-medium text-gray-900">{{ cluster.label }}</p>
              <p class="text-sm text-gray-500">{{ cluster.count }} employees</p>
            </div>
          </div>
          <div class="text-right">
            <p class="font-semibold text-gray-900">{{ cluster.percentage.toFixed(1) }}%</p>
          </div>
        </div>
        
        <div class="pt-4 border-t">
          <p class="text-sm text-gray-600">
            Total Analyzed: <span class="font-medium">{{ totalUsers }}</span> employees
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { Chart, ArcElement, Tooltip, Legend, type ChartConfiguration } from 'chart.js'

Chart.register(ArcElement, Tooltip, Legend)

interface ClusterData {
  label: string
  count: number
  percentage: number
}

interface Props {
  clusterData: ClusterData[]
  totalUsers: number
  accuracy: number
}

const props = defineProps<Props>()

const chartCanvas = ref<HTMLCanvasElement>()
let chart: Chart | null = null

const clusterColors = [
  '#ef4444', // red - Needs Improvement
  '#f59e0b', // amber - Average Performer  
  '#10b981', // emerald - Good Performer
  '#3b82f6', // blue - High Performer
]

const getClusterColor = (index: number) => {
  return clusterColors[index % clusterColors.length]
}

const createChart = async () => {
  if (!chartCanvas.value || props.clusterData.length === 0) return
  
  await nextTick()
  
  if (chart) {
    chart.destroy()
  }
  
  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return
  
  const config: ChartConfiguration = {
    type: 'doughnut',
    data: {
      labels: props.clusterData.map(c => c.label),
      datasets: [{
        data: props.clusterData.map(c => c.count),
        backgroundColor: props.clusterData.map((_, index) => getClusterColor(index)),
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverBorderWidth: 3,
        hoverBorderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.parsed
              const percentage = ((value / props.totalUsers) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      },
      cutout: '60%'
    }
  }
  
  chart = new Chart(ctx, config)
}

onMounted(() => {
  createChart()
})

watch(() => props.clusterData, () => {
  createChart()
}, { deep: true })
</script>