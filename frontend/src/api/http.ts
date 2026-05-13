import axios from 'axios'
import { camelToSnake } from '../utils/formatKeys'

const http = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use((config) => {
  if (config.data && typeof config.data === 'object') {
    config.data = camelToSnake(config.data)
  }
  if (config.params && typeof config.params === 'object') {
    config.params = camelToSnake(config.params)
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.message)
    return Promise.reject(error)
  }
)

export default http
