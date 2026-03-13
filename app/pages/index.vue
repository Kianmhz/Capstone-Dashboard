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

const config = useRuntimeConfig()
const pcVideoUrl  = config.public.pcAgentUrl
const piVideoUrl  = config.public.piAgentUrl

const globalLoading = computed(() => pc.value.loading && pi.value.loading)

onMounted(async () => {
  await refreshAll()
  startPolling(8000)
})

function clearLogs() {
  logs.value = []
}

const pcOnlineColor = computed(() => {
  if (pc.value.online === null) return 'neutral'
  return pc.value.online ? 'success' : 'error'
})

const piOnlineColor = computed(() => {
  if (pi.value.online === null) return 'neutral'
  return pi.value.online ? 'success' : 'error'
})
</script>

<template>
  <UApp>
    <UDashboardGroup>

      <!-- ── Sidebar ────────────────────────────────────────────────────────── -->
      <UDashboardSidebar>
        <template #header>
          <div class="flex items-center gap-3 px-1 py-1">
            <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10">
              <UIcon name="heroicons:signal" class="text-xl text-primary" />
            </div>
            <div>
              <p class="font-bold text-sm leading-none">Capstone</p>
              <p class="text-xs text-gray-400 mt-0.5">Control Dashboard</p>
            </div>
          </div>
        </template>

        <div class="px-2 space-y-5 py-2">

          <!-- Devices section -->
          <div class="space-y-1">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2 mb-2">Devices</p>

            <!-- PC row -->
            <div class="flex items-center gap-2.5 rounded-lg px-2 py-2 hover:bg-gray-800/50 transition-colors">
              <UChip :color="pcOnlineColor" inset size="sm" class="shrink-0">
                <UIcon name="heroicons:computer-desktop" class="text-xl text-gray-300" />
              </UChip>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium">Home PC</p>
                <div class="flex items-center gap-1 mt-0.5">
                  <UBadge
                    :color="pc.online ? 'success' : pc.online === false ? 'error' : 'neutral'"
                    variant="subtle"
                    size="xs"
                  >
                    {{ pc.online === null ? '—' : pc.online ? 'Online' : 'Offline' }}
                  </UBadge>
                  <UBadge
                    :color="pc.running ? 'info' : 'warning'"
                    variant="subtle"
                    size="xs"
                  >
                    {{ pc.running === null ? '—' : pc.running ? 'Running' : 'Stopped' }}
                  </UBadge>
                </div>
              </div>
            </div>

            <!-- Pi row -->
            <div class="flex items-center gap-2.5 rounded-lg px-2 py-2 hover:bg-gray-800/50 transition-colors">
              <UChip :color="piOnlineColor" inset size="sm" class="shrink-0">
                <UIcon name="heroicons:cpu-chip" class="text-xl text-gray-300" />
              </UChip>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium">Raspberry Pi</p>
                <div class="flex items-center gap-1 mt-0.5">
                  <UBadge
                    :color="pi.online ? 'success' : pi.online === false ? 'error' : 'neutral'"
                    variant="subtle"
                    size="xs"
                  >
                    {{ pi.online === null ? '—' : pi.online ? 'Online' : 'Offline' }}
                  </UBadge>
                  <UBadge
                    :color="pi.running ? 'info' : 'warning'"
                    variant="subtle"
                    size="xs"
                  >
                    {{ pi.running === null ? '—' : pi.running ? 'Running' : 'Stopped' }}
                  </UBadge>
                </div>
              </div>
            </div>
          </div>

          <USeparator />

          <!-- Global actions section -->
          <div class="space-y-2">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2 mb-2">Global Actions</p>
            <UButton
              block
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
              block
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
              block
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

        <template #footer>
          <div class="flex items-center gap-2 px-3 py-2 text-xs text-gray-500">
            <UIcon name="heroicons:clock" class="text-sm shrink-0" />
            <span>Auto-refresh every 8s · Proxied via Nuxt</span>
          </div>
        </template>
      </UDashboardSidebar>

      <!-- ── Main panel ─────────────────────────────────────────────────────── -->
      <UDashboardPanel>
        <template #header>
          <UDashboardNavbar title="Distributed Systems Demo" icon="heroicons:signal">
            <template #right>
              <span class="text-xs text-gray-400 hidden sm:block">March 2026</span>
            </template>
          </UDashboardNavbar>
        </template>

        <div class="p-4 sm:p-6 space-y-6 overflow-y-auto">

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

        </div>
      </UDashboardPanel>

    </UDashboardGroup>

    <UToaster />
  </UApp>
</template>
