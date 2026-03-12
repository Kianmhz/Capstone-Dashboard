<script setup>
// pages/index.vue
// Main control dashboard

const {
  pc,
  pi,
  fetchStatus,
  startDevice,
  stopDevice,
  refreshAll,
  startBoth,
  stopBoth,
  startPolling,
  logs,
} = useDevices()

const deviceRefs = {
  pc,
  pi,
}

function handleStart(deviceId) {
  return startDevice(deviceRefs[deviceId])
}

function handleStop(deviceId) {
  return stopDevice(deviceRefs[deviceId])
}

function handleRefresh(deviceId) {
  return fetchStatus(deviceRefs[deviceId])
}

// Expose device agent base URLs to the client so the video <img> src can
// point directly at the agent (avoids proxying a large MJPEG stream).
// These are public URLs — intentionally exposed via publicRuntimeConfig.
const config = useRuntimeConfig()
const pcVideoUrl  = config.public.pcAgentUrl
const piVideoUrl  = config.public.piAgentUrl

// Global loading flag
const globalLoading = computed(() => pc.value.loading && pi.value.loading)

// Initial fetch on mount, then start auto-poll
onMounted(async () => {
  await refreshAll()
  startPolling(8000)
})

function clearLogs() {
  logs.value = []
}
</script>

<template>
  <div class="min-h-screen bg-gray-950 text-gray-100">
    <UApp>

      <!-- ── Top navigation bar ──────────────────────────────────────────── -->
      <header class="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <UIcon name="heroicons:signal" class="text-2xl text-primary" />
            <div>
              <h1 class="text-base font-bold leading-none tracking-tight">Capstone Control Dashboard</h1>
              <p class="text-xs text-gray-400 mt-0.5">Distributed Systems Demo — March 2026</p>
            </div>
          </div>

          <!-- Global actions -->
          <div class="flex items-center gap-2 flex-wrap justify-end">
            <UButton
              color="success"
              variant="solid"
              icon="heroicons:play-circle"
              :loading="globalLoading"
              size="sm"
              @click="startBoth"
            >
              Start Both
            </UButton>
            <UButton
              color="error"
              variant="solid"
              icon="heroicons:stop-circle"
              :loading="globalLoading"
              size="sm"
              @click="stopBoth"
            >
              Stop Both
            </UButton>
            <UButton
              color="neutral"
              variant="outline"
              icon="heroicons:arrow-path"
              :loading="globalLoading"
              size="sm"
              @click="refreshAll"
            >
              Refresh All
            </UButton>
          </div>
        </div>
      </header>

      <!-- ── Main content ────────────────────────────────────────────────── -->
      <main class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        <!-- Status summary strip -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <UCard class="text-center py-2">
            <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">PC Online</p>
            <UIcon
              :name="pc.online ? 'heroicons:check-circle' : 'heroicons:x-circle'"
              :class="['text-3xl', pc.online ? 'text-green-400' : 'text-red-400']"
            />
          </UCard>
          <UCard class="text-center py-2">
            <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">PC Process</p>
            <UIcon
              :name="pc.running ? 'heroicons:play-circle' : 'heroicons:pause-circle'"
              :class="['text-3xl', pc.running ? 'text-blue-400' : 'text-gray-500']"
            />
          </UCard>
          <UCard class="text-center py-2">
            <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Pi Online</p>
            <UIcon
              :name="pi.online ? 'heroicons:check-circle' : 'heroicons:x-circle'"
              :class="['text-3xl', pi.online ? 'text-green-400' : 'text-red-400']"
            />
          </UCard>
          <UCard class="text-center py-2">
            <p class="text-xs text-gray-400 uppercase tracking-wider mb-1">Pi Process</p>
            <UIcon
              :name="pi.running ? 'heroicons:play-circle' : 'heroicons:pause-circle'"
              :class="['text-3xl', pi.running ? 'text-blue-400' : 'text-gray-500']"
            />
          </UCard>
        </div>

        <!-- Device cards -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DeviceCard
            :device="pc"
            :video-url="pcVideoUrl"
            @start="handleStart('pc')"
            @stop="handleStop('pc')"
            @refresh="handleRefresh('pc')"
          />
          <DeviceCard
            :device="pi"
            :video-url="piVideoUrl"
            @start="handleStart('pi')"
            @stop="handleStop('pi')"
            @refresh="handleRefresh('pi')"
          />
        </div>

        <!-- Logs panel -->
        <LogsPanel :logs="logs" @clear="clearLogs" />

        <!-- Footer -->
        <footer class="text-center text-gray-600 text-xs pb-4">
          Auto-refreshing every 8 s · All requests proxied through Nuxt server layer
        </footer>
      </main>

      <!-- Toast notifications rendered here -->
      <UToaster />
    </UApp>
  </div>
</template>
