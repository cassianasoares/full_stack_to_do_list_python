import React, { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

interface LocationState {
  from?: { pathname: string }
  justRegistered?: boolean
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuth()

  const state = (location.state as LocationState | null) ?? null
  const from = state?.from?.pathname ?? '/home'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success] = useState<string | null>(
    state?.justRegistered ? 'Conta criada com sucesso! Faça login para continuar.' : null,
  )

  useEffect(() => {
    if (state?.justRegistered) {
      navigate(location.pathname, { replace: true, state: { from: state.from } })
    }
  }, [state, location.pathname, navigate])

  async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    try {
      await login({ email: email.trim(), password })
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao autenticar.')
    }
  }

  return (
    <main className="auth-container" data-testid="login-page">
      <section className="auth-card">
        <h1>Entrar</h1>
        <p className="auth-subtitle">Acesse sua conta para continuar.</p>

        <form onSubmit={handleSubmit} noValidate data-testid="login-form">
          <label className="field">
            <span>E-mail</span>
            <input
              data-testid="login-email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="field">
            <span>Senha</span>
            <input
              data-testid="login-password"
              type="password"
              autoComplete="current-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && <p className="form-error" role="alert" data-testid="login-error">{error}</p>}

          {success && <p className="form-success" role="status" data-testid="login-success">{success}</p>}

          <button type="submit" className="primary-button" disabled={isLoading} data-testid="login-submit">
            {isLoading ? 'Entrando…' : 'Entrar'}
          </button>
        </form>

        <p className="auth-footer">
          Não tem conta? <Link to="/register" data-testid="login-register-link">Criar conta</Link>
        </p>
      </section>
    </main>
  )
}
