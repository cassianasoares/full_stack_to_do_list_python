import axios from 'axios'
import { api, extractErrorMessage } from './client'
import type { LoginPayload, RegisterPayload, User } from '../types/auth'

const AUTH_BASE = '/auth'

export async function register(payload: RegisterPayload): Promise<User> {
  try {
    const { data } = await api.post<User>(`${AUTH_BASE}/register/`, payload)
    return data
  } catch (err) {
    throw new Error(extractErrorMessage(err, 'Falha ao registrar usuário.'))
  }
}

export async function login(payload: LoginPayload): Promise<User> {
  try {
    const { data } = await api.post<User>(`${AUTH_BASE}/login/`, payload)
    return data
  } catch (err) {
    throw new Error(extractErrorMessage(err, 'Falha ao autenticar.'))
  }
}

export async function logout(): Promise<void> {
  try {
    await api.post(`${AUTH_BASE}/logout/`)
  } catch (err) {
    throw new Error(extractErrorMessage(err, 'Falha ao sair.'))
  }
}

export async function fetchMe(): Promise<User | null> {
  try {
    const { data } = await api.get<User>(`${AUTH_BASE}/me/`)
    return data
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 401) {
      return null
    }
    throw new Error(extractErrorMessage(err, 'Falha ao obter usuário.'))
  }
}
