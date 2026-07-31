import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { UserProvider, useUser } from './context/UserContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CreateMemoryPage from './pages/CreateMemoryPage'
import QueryPage from './pages/QueryPage'

function ProtectedRoute({ children }) {
  const { currentUser } = useUser()
  if (!currentUser) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  const { currentUser } = useUser()

  return (
    <Routes>
      <Route path="/login" element={
        currentUser ? <Navigate to="/dashboard" replace /> : <LoginPage />
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Layout><DashboardPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/create" element={
        <ProtectedRoute>
          <Layout><CreateMemoryPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/query" element={
        <ProtectedRoute>
          <Layout><QueryPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/memory/:memoryId" element={
        <ProtectedRoute>
          <Layout><CreateMemoryPage /></Layout>
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to={currentUser ? "/dashboard" : "/login"} replace />} />
    </Routes>
  )
}

function App() {
  return (
    <UserProvider>
      <Router>
        <AppRoutes />
      </Router>
    </UserProvider>
  )
}

export default App
