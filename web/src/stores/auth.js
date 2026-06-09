import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  // 解析 JWT payload
  function parseJwt(jwt) {
    try {
      return JSON.parse(atob(jwt.split('.')[1]))
    } catch {
      return null
    }
  }

  // 根据 JWT 中的 user_id 获取用户信息
  async function fetchUser() {
    const payload = parseJwt(token.value)
    if (!payload?.user_id) return
    try {
      const res = await request.get(`/pbapi/users/${payload.user_id}`)
      if (res.code === 200 && res.data) {
        user.value = res.data
      }
    } catch (e) {
      console.error('获取用户信息失败:', e)
    }
  }

  async function login(email, password) {
    const res = await request.post('/auth/sign-in', { email, password })
    if (res.code === 200 && res.data?.token) {
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)
      await fetchUser()
    }
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, login, logout, fetchUser }
})
