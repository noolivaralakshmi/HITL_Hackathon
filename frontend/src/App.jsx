import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { UserProvider } from './context/UserContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CreateMemoryPage from './pages/CreateMemoryPage'
import QueryPage from './pages/QueryPage'

function App() {
  return (
    <UserProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/create" element={<CreateMemoryPage />} />
            <Route path="/query" element={<QueryPage />} />
          </Routes>
        </Layout>
      </Router>
    </UserProvider>
  )
}

export default App
