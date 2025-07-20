<template>
  <div class="flex items-center space-x-4">
    <div class="flex items-center space-x-2">
      <label class="text-sm font-medium text-gray-700">From:</label>
      <input
        v-model="localDateFrom"
        type="date"
        class="border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
        @change="updateDates"
      />
    </div>
    
    <div class="flex items-center space-x-2">
      <label class="text-sm font-medium text-gray-700">To:</label>
      <input
        v-model="localDateTo"
        type="date"
        class="border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
        @change="updateDates"
      />
    </div>
    
    <div class="flex items-center space-x-2">
      <button
        @click="setCurrentMonth"
        class="btn-secondary text-sm px-3 py-1"
      >
        This Month
      </button>
      
      <button
        @click="setLastMonth"
        class="btn-secondary text-sm px-3 py-1"
      >
        Last Month
      </button>
      
      <button
        @click="clearDates"
        class="btn-secondary text-sm px-3 py-1"
      >
        All Time
      </button>
    </div>
    
    <button
      @click="applyFilter"
      :disabled="loading"
      class="btn-primary text-sm px-4 py-2"
    >
      <span v-if="loading" class="flex items-center">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading...
      </span>
      <span v-else>Apply Filter</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  dateFrom?: string
  dateTo?: string
  loading?: boolean
}

interface Emits {
  (e: 'update:dateFrom', value: string): void
  (e: 'update:dateTo', value: string): void
  (e: 'apply'): void
}

const props = withDefaults(defineProps<Props>(), {
  dateFrom: '',
  dateTo: '',
  loading: false
})

const emit = defineEmits<Emits>()

const localDateFrom = ref(props.dateFrom)
const localDateTo = ref(props.dateTo)

watch(() => props.dateFrom, (newVal) => {
  localDateFrom.value = newVal
})

watch(() => props.dateTo, (newVal) => {
  localDateTo.value = newVal
})

const updateDates = () => {
  emit('update:dateFrom', localDateFrom.value)
  emit('update:dateTo', localDateTo.value)
}

const setCurrentMonth = () => {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  
  localDateFrom.value = firstDay.toISOString().split('T')[0]
  localDateTo.value = lastDay.toISOString().split('T')[0]
  updateDates()
}

const setLastMonth = () => {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  const lastDay = new Date(now.getFullYear(), now.getMonth(), 0)
  
  localDateFrom.value = firstDay.toISOString().split('T')[0]
  localDateTo.value = lastDay.toISOString().split('T')[0]
  updateDates()
}

const clearDates = () => {
  localDateFrom.value = ''
  localDateTo.value = ''
  updateDates()
}

const applyFilter = () => {
  emit('apply')
}
</script>