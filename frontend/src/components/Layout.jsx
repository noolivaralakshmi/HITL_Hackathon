import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useUser } from '../context/UserContext'
import { Brain, Home, ChevronDown } from 'lucide-react'
import { useState } from 'react'

export default function Layout({ children }) {
  const { users, currentUser, switchUser } = useUser()
  const navigate = useNavigate()
  const location = useLocation()
  const [showRoleMenu, setShowRoleMenu] = useState(false)

  const roleColors = {
    admin: 'text-purple-400 bg-purple-500/20 border-purple-500/30',
    approver: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    reviewer: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    viewer: 'text-gray-400 bg-gray-500/20 border-gray-500/30',
  }

  return (
    <div className="min-h-screen gradient-mesh">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => navigate('/')}
          >
            <div className="w-10 h-10 bg-primary-600/20 rounded-xl flex items-center justify-center border border-primary-500/30">
              <Brain className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Change Impact Memory</h1>
              <p className="text-xs text-white/40">Enterprise Decision Intelligence</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => navigate('/')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                location.pathname === '/'
                  ? 'bg-white/10 text-white'
                  : 'text-white/50 hover:text-white hover:bg-white/5'
              }`}
            >
              <Home className="w-4 h-4 inline mr-2" />
              Home
            </button>
          </nav>

          {/* Role Selector */}
          <div className="relative">
            <button
              onClick={() => setShowRoleMenu(!showRoleMenu)}
              className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
            >
              <div className="text-right">
                <p className="text-sm font-medium text-white">{currentUser.name}</p>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${roleColors[currentUser.role]}`}>
                  {currentUser.role}
                </span>
              </div>
              <ChevronDown className="w-4 h-4 text-white/40" />
            </button>

            {showRoleMenu && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute right-0 mt-2 w-72 glass-card p-2 z-50"
              >
                <p className="px-3 py-2 text-xs font-semibold text-white/40 uppercase tracking-wider">
                  Switch Role (Demo)
                </p>
                {users.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => {
                      switchUser(user.id)
                      setShowRoleMenu(false)
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-all ${
                      currentUser.id === user.id
                        ? 'bg-primary-600/20 border border-primary-500/30'
                        : 'hover:bg-white/5'
                    }`}
                  >
                    <div>
                      <p className="text-sm font-medium text-white">{user.name}</p>
                      <p className="text-xs text-white/40">{user.email}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${roleColors[user.role]}`}>
                      {user.role}
                    </span>
                  </button>
                ))}
              </motion.div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  )
}
