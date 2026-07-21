import axios, { AxiosError, type AxiosInstance } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export const api: AxiosInstance = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
  // Required so the browser stores and sends the HttpOnly auth cookies
  // set by the backend (POST /api/auth/login/ and cleared by /logout/).
  withCredentials: true,
})

let onUnauthorized: (() => void) | null = null

export function registerUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      onUnauthorized?.()
    }
    return Promise.reject(error)
  },
)

export function extractErrorMessage(err: unknown, fallback = 'Ocorreu um erro inesperado.'): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as Record<string, unknown> | undefined
    if (data && typeof data === 'object') {
      if (typeof data.detail === 'string') return data.detail
      const firstKey = Object.keys(data)[0]
      if (firstKey) {
        const value = (data as Record<string, unknown>)[firstKey]
        if (Array.isArray(value) && value.length > 0) return String(value[0])
        if (typeof value === 'string') return value
      }
    }
    if (err.message) return err.message
  }
  return fallback
}
