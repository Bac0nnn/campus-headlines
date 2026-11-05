import request from './request'

export const mediaLogin = (data) => request.post('/media/auth/login', data)
export const getMediaMe = () => request.get('/media/auth/me')
export const updateMediaProfile = (data) => request.put('/media/auth/profile', data)
export const uploadMediaAvatar = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/media/auth/avatar', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getMaterials = (params) => request.get('/media/materials', { params })
export const uploadMaterial = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/media/materials', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const collectMaterial = (id) => request.put('/media/materials/' + id + '/collect')
export const deleteMaterial = (id) => request.delete('/media/materials/' + id)

export const createNews = (data) => request.post('/media/news', data)
export const updateNews = (id, data) => request.put('/media/news/' + id, data)
export const submitNews = (id) => request.post('/media/news/' + id + '/submit')
export const getMediaNews = (params) => request.get('/media/news', { params })
export const getMediaNewsDetail = (id) => request.get('/media/news/' + id)
export const deleteNews = (id) => request.delete('/media/news/' + id)

export const getAuditNews = (params) => request.get('/media/audit/news', { params })
export const getAuditNewsDetail = (id) => request.get('/media/audit/news/' + id)
export const reviewNews = (id, data) => request.post('/media/audit/news/' + id + '/review', data)
