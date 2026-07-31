import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useUser } from '../context/UserContext'
import { Brain, LayoutDashboard, Upload, MessageSquare, LogOut, User } from 'lucide-react'

export default function Layout({ children }) {
  const { currentUser, logout, isReviewer } = useUser()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/create', label: 'Create Memory', icon: Upload },
    { path: '/query', label: 'Ask Knowledge', icon: MessageSquare },
  ]

  return (
    <div className="min-h-screen gradient-mesh">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-surface-950/90 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => navigate('/dashboard')}
            >
              <div className="w-9 h-9 bg-gradient-to-br from-primary-600/30 to-violet-600/20 rounded-lg flex items-center justify-center border border-primary-500/30">
                <Brain className="w-5 h-5 text-primary-400" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-sm font-bold text-white leading-tight">Change Impact Memory</h1>
                <p className="text-[10px] text-white/30">Enterprise Decision Intelligence</p>
              </div>
            </div>

            {/* Navigation - removed, using quick access cards on dashboard instead */}

            {/* Navigation */}
            <nav className="flex items-center gap-2">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path ||
                  (item.path === '/create' && location.pathname.startsWith('/memory/'))
                return (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={`flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-600/20 text-white border border-primary-500/40'
                        : 'text-white/50 hover:text-white hover:bg-white/[0.06] border border-transparent'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </nav>

            {/* User Profile */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-600/40 to-violet-600/30 flex items-center justify-center">
                  <User className="w-4 h-4 text-white/80" />
                </div>
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-white leading-tight">{currentUser?.name}</p>
                  <span className={`text-[10px] font-medium ${
                    isReviewer ? 'text-purple-300' : 'text-emerald-300'
                  }`}>
                    {isReviewer ? 'Contributor + Reviewer' : 'Contributor'}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors text-red-400 hover:text-red-300 text-sm flex items-center gap-1.5"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  )
}
