import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Mail, ArrowRight, Shield } from 'lucide-react'
import { useUser } from '../context/UserContext'
import api from '../api/client'

export default function LoginPage() {
  const { login } = useUser()
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!email.trim()) return
    setError('')
    setIsLoading(true)

    try {
      const res = await api.post('/users/login', { email: email.trim() })
      login(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please use a registered email.')
    }
    setIsLoading(false)
  }

  const demoUsers = [
    { name: 'Vara Lakshmi', email: 'vara.lakshmi@company.com', role: 'Reviewer' },
    { name: 'Shanthi', email: 'shanthi@company.com', role: 'Reviewer' },
    { name: 'Archana', email: 'archana@company.com', role: 'Contributor' },
    { name: 'Priyanka', email: 'priyanka@company.com', role: 'Contributor' },
  ]

  return (
    <div className="min-h-screen gradient-mesh flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary-600/20 rounded-2xl flex items-center justify-center border border-primary-500/30">
            <Brain className="w-8 h-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold text-white">Change Impact Memory</h1>
          <p className="text-white/40 mt-2">Enterprise Decision Intelligence</p>
        </div>

        {/* Login Card */}
        <div className="glass-card p-8">
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">SSO Login</h2>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm text-white/60 block mb-2">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="input-field pl-10"
                  autoFocus
                />
              </div>
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2"
              >
                {error}
              </motion.p>
            )}

            <button
              type="submit"
              disabled={!email.trim() || isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Demo Quick Login */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-xs text-white/40 mb-3 uppercase tracking-wider font-medium">Quick Login (Demo)</p>
            <div className="grid grid-cols-2 gap-2">
              {demoUsers.map((user) => (
                <button
                  key={user.email}
                  onClick={() => setEmail(user.email)}
                  className="text-left p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all"
                >
                  <p className="text-sm text-white font-medium">{user.name}</p>
                  <p className="text-xs text-white/40">{user.role}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
