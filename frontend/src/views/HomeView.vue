<template>
  <AppLayout>
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center max-w-sm">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gray-800 border border-gray-700 mb-6">
          <svg class="w-10 h-10 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-white mb-2">Select an agent</h2>
        <p class="text-sm text-gray-500">Choose an agent from the sidebar, or create a new one to get started.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/AppLayout.vue'
</script>
