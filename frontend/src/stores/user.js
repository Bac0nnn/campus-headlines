import { defineStore } from 'pinia'
import { getUserMe } from '@/api/auth'

const TOKEN_KEY = 'campus_user_token'
const PROFILE_KEY = 'campus_user_profile'

function readProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY) || 'null')
  } catch (e) {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    profile: readProfile()
  }),
  getters: {
    isLogin: (state) => Boolean(state.token),
    displayName: (state) => state.profile?.name || '同学',
    avatar: (state) => state.profile?.avatar || '/avatars/u1.svg'
  },
  actions: {
    setLogin(data) {
      this.token = data.token
      this.profile = data
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem(PROFILE_KEY, JSON.stringify(data))
    },
    setProfile(profile) {
      this.profile = { ...this.profile, ...profile }
      localStorage.setItem(PROFILE_KEY, JSON.stringify(this.profile))
    },
    async refresh() {
      if (!this.token) return
      try {
        const me = await getUserMe()
        this.profile = { ...this.profile, ...me }
        localStorage.setItem(PROFILE_KEY, JSON.stringify(this.profile))
      } catch (e) {
        this.logout()
      }
    },
    logout() {
      this.token = ''
      this.profile = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(PROFILE_KEY)
    }
  }
})
