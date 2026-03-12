<script setup>
// components/DeviceCard.vue
// Renders a single device control card

const props = defineProps({
  device: {
    type: Object,
    required: true,
  },
  videoUrl: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['start', 'stop', 'refresh'])

// ── derived display values ────────────────────────────────────────────────────

const onlineBadgeColor = computed(() => {
  if (props.device.online === null) return 'neutral'
  return props.device.online ? 'success' : 'error'
})

const onlineBadgeLabel = computed(() => {
  if (props.device.online === null) return 'Unknown'
  return props.device.online ? 'Online' : 'Offline'
})

const runningBadgeColor = computed(() => {
  if (props.device.running === null) return 'neutral'
  return props.device.running ? 'info' : 'warning'
})

const runningBadgeLabel = computed(() => {
  if (props.device.running === null) return 'Unknown'
  return props.device.running ? 'Running' : 'Stopped'
})

// Video preview: show only if device is known to be online
const showVideo = computed(() => props.device.online === true)

// Append cache-buster so the <img> re-fetches after a hard refresh
const videoSrc = computed(() => `${props.videoUrl}/video_feed`)

const isExpanded = ref(false)
const expandedVideoContainer = ref(null)

function openExpanded() {
  if (!showVideo.value) return
  isExpanded.value = true
}

async function closeExpanded() {
  isExpanded.value = false

  if (!import.meta.client) return
  if (document.fullscreenElement && document.exitFullscreen) {
    try {
      await document.exitFullscreen()
    } catch {
      // Ignore browser-specific fullscreen exit issues.
    }
  }
}

async function toggleExpandedFullscreen() {
  if (!import.meta.client) return
  const container = expandedVideoContainer.value
  if (!container) return

  try {
    if (document.fullscreenElement && document.exitFullscreen) {
      await document.exitFullscreen()
      return
    }

    if (container.requestFullscreen) {
      await container.requestFullscreen()
      return
    }

    if (container.webkitRequestFullscreen) {
      container.webkitRequestFullscreen()
    }
  } catch {
    // Fallback is the expanded overlay itself.
  }
}

function onGlobalKeydown(event) {
  if (event.key === 'Escape' && isExpanded.value) {
    closeExpanded()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<template>
  <UCard class="h-full flex flex-col">
    <!-- ── Header ─────────────────────────────────────────────────────────── -->
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <UIcon :name="device.icon" class="text-2xl shrink-0 text-primary" />
          <span class="font-semibold text-lg truncate">{{ device.label }}</span>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <UBadge :color="onlineBadgeColor" variant="subtle" size="sm">
            {{ onlineBadgeLabel }}
          </UBadge>
          <UBadge :color="runningBadgeColor" variant="subtle" size="sm">
            {{ runningBadgeLabel }}
          </UBadge>
        </div>
      </div>
    </template>

    <!-- ── Body ──────────────────────────────────────────────────────────── -->
    <div class="flex flex-col gap-4 flex-1">

      <!-- Video Preview -->
      <div class="rounded-lg overflow-hidden bg-gray-900 border border-gray-700 aspect-video flex items-center justify-center relative">
        <template v-if="showVideo">
          <img
            :src="videoSrc"
            alt="Video feed"
            class="w-full h-full object-cover"
          />
          <span class="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-2 py-0.5 rounded uppercase tracking-wider flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-white rounded-full animate-pulse inline-block"></span>
            Live
          </span>
          <UButton
            size="xs"
            color="neutral"
            variant="solid"
            icon="heroicons:arrows-pointing-out"
            class="absolute top-2 right-2"
            @click.stop="openExpanded"
          >
            Expand
          </UButton>
        </template>
        <template v-else>
          <div class="flex flex-col items-center gap-2 text-gray-500">
            <UIcon name="heroicons:video-camera-slash" class="text-4xl" />
            <span class="text-sm">Feed unavailable</span>
          </div>
        </template>
      </div>

      <!-- Error alert -->
      <UAlert
        v-if="device.error"
        color="error"
        variant="subtle"
        :description="device.error"
        icon="heroicons:exclamation-triangle"
      />

      <!-- Action buttons -->
      <div class="flex items-center gap-2 flex-wrap">
        <UButton
          color="success"
          variant="solid"
          icon="heroicons:play"
          :loading="device.loading"
          :disabled="device.loading || device.running === true"
          class="flex-1"
          @click="emit('start')"
        >
          Start
        </UButton>

        <UButton
          color="error"
          variant="solid"
          icon="heroicons:stop"
          :loading="device.loading"
          :disabled="device.loading || device.running === false"
          class="flex-1"
          @click="emit('stop')"
        >
          Stop
        </UButton>

        <UButton
          color="neutral"
          variant="outline"
          icon="heroicons:arrow-path"
          :loading="device.loading"
          :disabled="device.loading"
          @click="emit('refresh')"
        />
      </div>
    </div>
  </UCard>

  <Teleport to="body">
    <div
      v-if="isExpanded"
      class="fixed inset-0 z-100 bg-black/90 p-4 sm:p-6 flex flex-col"
      @click.self="closeExpanded"
    >
      <div class="mx-auto w-full max-w-6xl flex items-center justify-between gap-3 text-gray-100">
        <div class="flex items-center gap-2 min-w-0">
          <UIcon :name="device.icon" class="text-xl shrink-0 text-primary" />
          <span class="font-semibold truncate">{{ device.label }} Live Feed</span>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <UButton
            color="neutral"
            variant="solid"
            size="sm"
            icon="heroicons:arrows-pointing-out"
            @click="toggleExpandedFullscreen"
          >
            Fullscreen
          </UButton>
          <UButton
            color="error"
            variant="solid"
            size="sm"
            icon="heroicons:x-mark"
            @click="closeExpanded"
          >
            Close
          </UButton>
        </div>
      </div>

      <div class="mx-auto mt-4 w-full max-w-6xl flex-1 min-h-0">
        <div
          ref="expandedVideoContainer"
          class="h-full w-full rounded-lg overflow-hidden bg-black border border-gray-700 flex items-center justify-center"
        >
          <img
            :src="videoSrc"
            :alt="`${device.label} video feed`"
            class="w-full h-full object-contain"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>
