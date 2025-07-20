<template>
  <div class="stat-card">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900">{{ value }}</p>
        <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
      </div>
      <div class="flex-shrink-0">
        <div :class="iconBgClass" class="w-12 h-12 rounded-lg flex items-center justify-center">
          <component :is="icon" :class="iconClass" class="w-6 h-6" />
        </div>
      </div>
    </div>
    <div v-if="trend" class="mt-4 flex items-center">
      <div :class="trendClass" class="flex items-center text-sm font-medium">
        <component :is="trendIcon" class="w-4 h-4 mr-1" />
        {{ trend }}
      </div>
      <span class="text-gray-500 text-sm ml-2">{{ trendLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  TrendingUpIcon, 
  TrendingDownIcon,
  UsersIcon,
  ClockIcon,
  ChartBarIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon?: any
  trend?: string
  trendLabel?: string
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue'
})

const iconBgClass = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    yellow: 'bg-yellow-100',
    red: 'bg-red-100',
    purple: 'bg-purple-100'
  }
  return colors[props.color]
})

const iconClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600',
    purple: 'text-purple-600'
  }
  return colors[props.color]
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  
  const isPositive = props.trend.startsWith('+') || !props.trend.startsWith('-')
  return isPositive ? 'text-green-600' : 'text-red-600'
})

const trendIcon = computed(() => {
  if (!props.trend) return null
  
  const isPositive = props.trend.startsWith('+') || !props.trend.startsWith('-')
  return isPositive ? TrendingUpIcon : TrendingDownIcon
})
</script>