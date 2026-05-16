import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useRestartStore = defineStore('restart', () => {
  const restartRequired = ref(false)
  const restarting = ref(false)

  function markRestartRequired() {
    restartRequired.value = true
  }

  async function handleRestart() {
    restarting.value = true
    try {
      await request.post('/pbapi/restart')
      for (let i = 0; i < 10; i++) {
        await new Promise(r => setTimeout(r, 1000))
        try {
          await request.get('/pbapi/config')
          restartRequired.value = false
          restarting.value = false
          return { status: 'completed' }
        } catch { /* 服务还在重启中 */ }
      }
      restarting.value = false
      return { status: 'timeout' }
    } catch (e) {
      restarting.value = false
      return { status: 'error', message: e.message }
    }
  }

  return { restartRequired, restarting, markRestartRequired, handleRestart }
})
