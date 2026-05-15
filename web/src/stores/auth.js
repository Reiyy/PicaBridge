import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')

  async function login(email, password) {
    const res = await request.post('/auth/sign-in', { email, password })
    token.value = res.data.token
    localStorage.setItem('token', res.data.token)
    return res
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
  }

  return { token, login, logout }
})
