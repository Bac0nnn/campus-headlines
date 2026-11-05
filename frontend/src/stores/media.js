import { defineStore } from 'pinia'
import { getMediaMe } from '@/api/media'

const TOKEN_KEY = 'campus_media_token'
const PROFILE_KEY = 'campus_media_profile'

function readProfile() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY) || 'null')
  } catch (e) {
    return null
  }
}

export const useMediaStore = defineStore('media', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    profile: readProfile()
  }),
  getters: {
    isLogin: (state) => Boolean(state.token),
    displayName: (state) => state.profile?.name || '校园媒体',
    avatar: (state) => state.profile?.avatar || '/avatars/m1.svg'
  },
  actions: {
    setLogin(data) {
      this.token = data.token
      this.profile = data
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem(PROFILE_KEY, JSON.stringify(data))
    },
    async refresh() {
      if (!this.token) return
      try {
        const me = await getMediaMe()
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
