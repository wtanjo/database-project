import axios from 'axios'

// 创建 axios 实例
const service = axios.create({
  baseURL: '', // 走代理
  timeout: 5000
})

// 1. 提交爬取任务
export function createTask(url: string) {
  return service.post('/api/tasks', { url })
}

// 2. 获取爬取结果 (对应 A 的 contents.py)
export function getContents() {
  return service.get('/api/contents')
}