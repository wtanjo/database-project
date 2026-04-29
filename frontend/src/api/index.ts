import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error('请求错误:', err)
    return Promise.reject(err)
  },
)

// ── Tasks ─────────────────────────────────────────────────────────────────────
export const createTask = (target_url: string) =>
  http.post('/tasks', { target_url })

export const getTasks = (page = 1, page_size = 10) =>
  http.get('/tasks', { params: { page, page_size } })

// ── Contents ──────────────────────────────────────────────────────────────────
export const getContents = (params: {
  keyword?: string
  start_time?: string
  end_time?: string
  page?: number
  page_size?: number
}) => http.get('/contents', { params })

export const exportContentsCSV = (params: {
  keyword?: string
  start_time?: string
  end_time?: string
}) => {
  const query = new URLSearchParams()
  if (params.keyword) query.append('keyword', params.keyword)
  if (params.start_time) query.append('start_time', params.start_time)
  if (params.end_time) query.append('end_time', params.end_time)
  window.open(`/api/contents/export/csv?${query.toString()}`)
}

// ── Images ────────────────────────────────────────────────────────────────────
export const getImages = (params: { keyword?: string; page?: number; page_size?: number }) =>
  http.get('/images', { params })

// ── Websites ──────────────────────────────────────────────────────────────────
export const getWebsites = (page = 1, page_size = 10) =>
  http.get('/websites', { params: { page, page_size } })

// ── Webpages ──────────────────────────────────────────────────────────────────
export const getWebpages = (params: { website_id?: number; page?: number; page_size?: number }) =>
  http.get('/webpages', { params })

export const deleteWebpage = (id: number) => http.delete(`/webpages/${id}`)

// ── Stats ─────────────────────────────────────────────────────────────────────
export const getStats = () => http.get('/stats')
