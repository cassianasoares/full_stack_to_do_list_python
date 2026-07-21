import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { HomePage } from './pages/HomePage'
import { GuestRoute, ProtectedRoute } from './routes/ProtectedRoute'

function Bootstrap({ children }: { children: React.ReactNode }) {
  const { isBootstrapping } = useAuth()
  if (isBootstrapping) {
    return (
      <main className="home-container">
        <p>Carregando…</p>
      </main>
    )
  }
  return <>{children}</>
}

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Bootstrap>
          <Routes>
            <Route
              path="/login"
              element={
                <GuestRoute>
                  <LoginPage />
                </GuestRoute>
              }
            />
            <Route
              path="/register"
              element={
                <GuestRoute>
                  <RegisterPage />
                </GuestRoute>
              }
            />
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Bootstrap>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
