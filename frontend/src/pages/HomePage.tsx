import { useAuth } from '../context/AuthContext'

export function HomePage() {
  const { user, logout } = useAuth()
  const displayName = user
    ? `${user.first_name} ${user.last_name}`.trim() || user.username
    : ''

  return (
    <main className="home-container" data-testid="home-page">
      <h1 data-testid="home-welcome">Bem-vindo{displayName ? `, ${displayName}` : ''}!</h1>
      <button type="button" className="secondary-button" onClick={logout} data-testid="home-logout">
        Sair
      </button>
    </main>
  )
}
