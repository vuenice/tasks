<template>
  <div class="flex h-screen bg-gray-950 overflow-hidden">
    <Sidebar />
    <main class="flex-1 flex flex-col overflow-hidden bg-gray-900">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
</script>
