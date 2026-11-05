import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 20000
})

service.interceptors.request.use((config) => {
  const isMedia = (config.url || '').startsWith('/media')
  const token = isMedia
    ? localStorage.getItem('campus_media_token')
    : localStorage.getItem('campus_user_token')
  if (token) {
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res.data
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message
    if (status === 401) {
      ElMessage.warning(message || '请先登录')
    } else {
      ElMessage.error(message || '网络异常，请稍后再试')
    }
    return Promise.reject(error)
  }
)

export default service
