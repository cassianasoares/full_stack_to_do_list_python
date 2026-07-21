export interface User {
  id: number
  first_name: string
  last_name: string
  username: string
  email: string
  role: string | null
}

export interface RegisterPayload {
  first_name: string
  last_name: string
  username: string
  email: string
  role?: string
  password: string
  password_match: string
}

export interface LoginPayload {
  email: string
  password: string
}
