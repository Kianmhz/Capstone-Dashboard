// composables/useDevices.js
// Central state and actions for both device agents

/** @returns {import('vue').Ref<import('../app/types/index').LogEntry[]>} */
export const useDeviceLogs = () => useState('device-logs', () => [])

// ─── helpers ──────────────────────────────────────────────────────────────────

function makeDevice(id, label, icon) {
  return {
    id,
    label,
    icon,
    online: null,   // null = not yet fetched
    running: null,
    loading: false,
    error: null,
  }
}

function appendLog(logs, message, type = 'info') {
  logs.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    timestamp: new Date(),
    message,
    type,
  })
  // Keep log list from growing forever in the UI
  if (logs.value.length > 200) logs.value = logs.value.slice(0, 200)
}

// ─── composable ───────────────────────────────────────────────────────────────

export function useDevices() {
  const toast = useToast()
  const logs = useDeviceLogs()

  const pc = useState('device-pc', () => makeDevice('pc', 'Home PC', 'heroicons:computer-desktop'))
  const pi = useState('device-pi', () => makeDevice('pi', 'Raspberry Pi', 'heroicons:cpu-chip'))

  // ── fetch status ────────────────────────────────────────────────────────────

  async function fetchStatus(device) {
    device.value.loading = true
    device.value.error = null
    try {
      const data = await $fetch(`/api/devices/${device.value.id}/status`)
      device.value.online = data.online ?? false
      device.value.running = data.running ?? false
      if (data._error) {
        device.value.online = false
        device.value.running = false
        device.value.error = data._error
        appendLog(logs, `${device.value.label} appears offline — ${data._error}`, 'error')
      } else {
        appendLog(logs, `${device.value.label} status refreshed`, 'info')
      }
    } catch (err) {
      device.value.online = false
      device.value.running = false
      device.value.error = err?.message || 'Unknown error'
      appendLog(logs, `${device.value.label} status check failed — ${device.value.error}`, 'error')
      toast.add({ title: `${device.value.label} unreachable`, description: device.value.error, color: 'error' })
    } finally {
      device.value.loading = false
    }
  }

  // ── start ────────────────────────────────────────────────────────────────────

  async function startDevice(device) {
    device.value.loading = true
    device.value.error = null
    try {
      const res = await $fetch(`/api/devices/${device.value.id}/start`, { method: 'POST' })
      if (res.success) {
        appendLog(logs, `${device.value.label} started successfully`, 'success')
        toast.add({ title: `${device.value.label} started`, color: 'success' })
      } else {
        appendLog(logs, `${device.value.label} start failed — ${res.error}`, 'error')
        toast.add({ title: `${device.value.label} start failed`, description: res.error, color: 'error' })
        device.value.error = res.error
      }
    } catch (err) {
      const msg = err?.message || 'Unknown error'
      appendLog(logs, `${device.value.label} start error — ${msg}`, 'error')
      toast.add({ title: `${device.value.label} error`, description: msg, color: 'error' })
      device.value.error = msg
    } finally {
      device.value.loading = false
      // Refresh status after action so badges update
      await fetchStatus(device)
    }
  }

  // ── stop ─────────────────────────────────────────────────────────────────────

  async function stopDevice(device) {
    device.value.loading = true
    device.value.error = null
    try {
      const res = await $fetch(`/api/devices/${device.value.id}/stop`, { method: 'POST' })
      if (res.success) {
        appendLog(logs, `${device.value.label} stopped successfully`, 'success')
        toast.add({ title: `${device.value.label} stopped`, color: 'success' })
      } else {
        appendLog(logs, `${device.value.label} stop failed — ${res.error}`, 'error')
        toast.add({ title: `${device.value.label} stop failed`, description: res.error, color: 'error' })
        device.value.error = res.error
      }
    } catch (err) {
      const msg = err?.message || 'Unknown error'
      appendLog(logs, `${device.value.label} stop error — ${msg}`, 'error')
      toast.add({ title: `${device.value.label} error`, description: msg, color: 'error' })
      device.value.error = msg
    } finally {
      device.value.loading = false
      await fetchStatus(device)
    }
  }

  // ── global helpers ──────────────────────────────────────────────────────────

  async function refreshAll() {
    appendLog(logs, 'Refreshing all device statuses…', 'info')
    await Promise.all([fetchStatus(pc), fetchStatus(pi)])
  }

  async function startBoth() {
    appendLog(logs, 'Starting all devices…', 'info')
    await Promise.all([startDevice(pc), startDevice(pi)])
  }

  async function stopBoth() {
    appendLog(logs, 'Stopping all devices…', 'warning')
    await Promise.all([stopDevice(pc), stopDevice(pi)])
  }

  // ── auto-refresh ─────────────────────────────────────────────────────────────

  function startPolling(intervalMs = 8000) {
    const timer = setInterval(() => {
      fetchStatus(pc)
      fetchStatus(pi)
    }, intervalMs)
    onUnmounted(() => clearInterval(timer))
    return timer
  }

  return {
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
  }
}
