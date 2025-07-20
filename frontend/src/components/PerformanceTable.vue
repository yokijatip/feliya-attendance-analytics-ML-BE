<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      <div class="flex items-center space-x-2">
        <select 
          v-model="sortBy" 
          class="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="performance_score">Performance Score</option>
          <option value="attendance_rate">Attendance Rate</option>
          <option value="productivity_score">Productivity Score</option>
          <option value="punctuality_score">Punctuality Score</option>
        </select>
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Employee
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cluster
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Performance
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Attendance
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Punctuality
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Productivity
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(employee, index) in sortedEmployees" :key="employee.user_id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ getInitials(employee.name) }}
                    </span>
                  </div>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ employee.name }}</div>
                  <div class="text-sm text-gray-500">{{ employee.worker_id }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getClusterBadgeClass(employee.cluster_label)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                {{ employee.cluster_label }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-1">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-primary-600 h-2 rounded-full" 
                      :style="{ width: `${Math.min(employee.performance_score, 100)}%` }"
                    ></div>
                  </div>
                </div>
                <span class="ml-2 text-sm font-medium text-gray-900">
                  {{ employee.performance_score.toFixed(1) }}
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ employee.features.attendance_rate?.toFixed(1) || 0 }}%
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ employee.features.punctuality_score?.toFixed(1) || 0 }}%
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ employee.features.productivity_score?.toFixed(1) || 0 }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="employees.length === 0" class="text-center py-12">
      <div class="text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm text-gray-500">No employee data available</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ClusteringResult } from '@/services/api'

interface Props {
  employees: ClusteringResult[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Employee Performance Analysis'
})

const sortBy = ref<string>('performance_score')

const sortedEmployees = computed(() => {
  return [...props.employees].sort((a, b) => {
    if (sortBy.value === 'performance_score') {
      return b.performance_score - a.performance_score
    } else {
      const aValue = a.features[sortBy.value] || 0
      const bValue = b.features[sortBy.value] || 0
      return bValue - aValue
    }
  })
})

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getClusterBadgeClass = (clusterLabel: string) => {
  const classes = {
    'High Performer': 'bg-green-100 text-green-800',
    'Good Performer': 'bg-blue-100 text-blue-800',
    'Average Performer': 'bg-yellow-100 text-yellow-800',
    'Needs Improvement': 'bg-red-100 text-red-800'
  }
  return classes[clusterLabel as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}
</script>