import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const MIN_PASSWORD = 8

export function RegisterPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { register, isLoading } = useAuth()

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    role: '',
    password: '',
    password_match: '',
  })
  const [error, setError] = useState<string | null>(null)

  function update<K extends keyof typeof form>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (form.password !== form.password_match) {
      setError('As senhas não coincidem.')
      return
    }
    if (form.password.length < MIN_PASSWORD) {
      setError(`A senha deve ter no mínimo ${MIN_PASSWORD} caracteres.`)
      return
    }

    try {
      await register({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        username: form.username.trim(),
        email: form.email.trim(),
        role: form.role.trim() || undefined,
        password: form.password,
        password_match: form.password_match,
      })
      navigate('/login', {
        replace: true,
        state: { from: (location.state as { from?: { pathname: string } } | null)?.from, justRegistered: true },
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao registrar usuário.')
    }
  }

  return (
    <main className="auth-container" data-testid="register-page">
      <section className="auth-card">
        <h1>Criar conta</h1>
        <p className="auth-subtitle">Preencha seus dados para se registrar.</p>

        <form onSubmit={handleSubmit} noValidate data-testid="register-form">
          <div className="field-row">
            <label className="field">
              <span>Nome</span>
              <input
                data-testid="register-first-name"
                type="text"
                required
                value={form.first_name}
                onChange={(e) => update('first_name', e.target.value)}
              />
            </label>
            <label className="field">
              <span>Sobrenome</span>
              <input
                data-testid="register-last-name"
                type="text"
                required
                value={form.last_name}
                onChange={(e) => update('last_name', e.target.value)}
              />
            </label>
          </div>

          <label className="field">
            <span>Usuário</span>
            <input
              data-testid="register-username"
              type="text"
              required
              value={form.username}
              onChange={(e) => update('username', e.target.value)}
            />
          </label>

          <label className="field">
            <span>E-mail</span>
            <input
              data-testid="register-email"
              type="email"
              autoComplete="email"
              required
              value={form.email}
              onChange={(e) => update('email', e.target.value)}
            />
          </label>

          <label className="field">
            <span>Função (opcional)</span>
            <input
              data-testid="register-role"
              type="text"
              value={form.role}
              onChange={(e) => update('role', e.target.value)}
              placeholder="Ex.: admin, member"
            />
          </label>

          <div className="field-row">
            <label className="field">
              <span>Senha</span>
              <input
                data-testid="register-password"
                type="password"
                autoComplete="new-password"
                required
                minLength={MIN_PASSWORD}
                value={form.password}
                onChange={(e) => update('password', e.target.value)}
              />
            </label>
            <label className="field">
              <span>Confirmar senha</span>
              <input
                data-testid="register-password-match"
                type="password"
                autoComplete="new-password"
                required
                minLength={MIN_PASSWORD}
                value={form.password_match}
                onChange={(e) => update('password_match', e.target.value)}
              />
            </label>
          </div>

          {error && <p className="form-error" role="alert" data-testid="register-error">{error}</p>}

          <button type="submit" className="primary-button" disabled={isLoading} data-testid="register-submit">
            {isLoading ? 'Criando conta…' : 'Criar conta'}
          </button>
        </form>

        <p className="auth-footer">
          Já tem conta? <Link to="/login" data-testid="register-login-link">Entrar</Link>
        </p>
      </section>
    </main>
  )
}
