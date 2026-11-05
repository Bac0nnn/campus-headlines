import request from './request'

export const sendCode = (phone) => request.post('/auth/send-code', null, { params: { phone } })
export const phoneLogin = (data) => request.post('/auth/login', data)
export const passwordLogin = (data) => request.post('/auth/login/password', data)
export const register = (data) => request.post('/auth/register', data)
export const getUserMe = () => request.get('/auth/me')
export const updateProfile = (data) => request.put('/auth/profile', data)
export const uploadAvatar = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/auth/avatar', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const userLogout = () => request.post('/auth/logout')
