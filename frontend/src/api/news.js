import request from './request'

export const getChannels = () => request.get('/channels')
export const getChannelStats = () => request.get('/channels/stats')
export const getNewsList = (params) => request.get('/news', { params })
export const getNewsDetail = (id) => request.get('/news/' + id)
export const toggleLike = (id) => request.post('/news/' + id + '/like')
export const getComments = (id) => request.get('/news/' + id + '/comments')
export const addComment = (id, content) => request.post('/news/' + id + '/comments', { content })
