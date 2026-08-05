import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Mail, ArrowRight, Shield, Lock } from 'lucide-react'
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
    { name: 'Vara Lakshmi', email: 'vara.lakshmi@company.com', role: 'Contributor + Reviewer', color: 'border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10' },
    { name: 'Shanthi', email: 'shanthi@company.com', role: 'Contributor + Reviewer', color: 'border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10' },
    { name: 'Archana', email: 'archana@company.com', role: 'Contributor', color: 'border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/10' },
    { name: 'Priyanka', email: 'priyanka@company.com', role: 'Contributor', color: 'border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/10' },
  ]

  return (
    <div className="min-h-screen gradient-mesh flex items-center justify-center px-4">
      {/* Background decorations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-600/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-lg relative z-10"
      >
        {/* Logo & Title */}
        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-primary-600/30 to-violet-600/20 rounded-2xl flex items-center justify-center border border-primary-500/30 shadow-lg shadow-primary-600/10"
          >
            <Brain className="w-10 h-10 text-primary-400" />
          </motion.div>
          <h1 className="text-4xl font-bold text-white tracking-tight">Change Impact Memory</h1>
          <p className="text-white/40 mt-3 text-lg">Enterprise Decision Intelligence Platform</p>
          <div className="flex items-center justify-center gap-2 mt-4">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-emerald-300/70">Human-in-the-Loop AI System</span>
          </div>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/[0.03] backdrop-blur-xl border border-white/[0.08] rounded-2xl p-8 shadow-2xl"
        >
          <div className="flex items-center gap-2 mb-6">
            <Lock className="w-4 h-4 text-white/40" />
            <h2 className="text-sm font-medium text-white/60 uppercase tracking-wider">Single Sign-On</h2>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm text-white/50 block mb-2 font-medium">Work Email Address</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl pl-11 pr-4 py-3.5 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/40 transition-all"
                  autoFocus
                />
              </div>
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3"
              >
                {error}
              </motion.p>
            )}

            <button
              type="submit"
              disabled={!email.trim() || isLoading}
              className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-3.5 rounded-xl transition-all duration-200 shadow-lg shadow-primary-600/25 hover:shadow-primary-500/40 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Continue with SSO <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Demo Quick Login */}
          <div className="mt-8 pt-6 border-t border-white/[0.06]">
            <p className="text-xs text-white/30 mb-4 uppercase tracking-wider font-medium">Demo Accounts</p>
            <div className="grid grid-cols-2 gap-3">
              {demoUsers.map((user) => (
                <button
                  key={user.email}
                  onClick={() => { setEmail(user.email); setError('') }}
                  className={`text-left p-3.5 rounded-xl border transition-all duration-200 ${user.color}`}
                >
                  <p className="text-sm text-white font-medium">{user.name}</p>
                  <p className="text-xs text-white/40 mt-0.5">{user.role}</p>
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        <p className="text-center text-xs text-white/20 mt-6">
          Protected by AWS Bedrock Guardrails · SOC 2 Compliant
        </p>
      </motion.div>
    </div>
  )
}
