import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Upload, MessageSquare, ArrowRight, Sparkles, Shield } from 'lucide-react'
import { loadDemo } from '../api/client'
import { useState } from 'react'

export default function HomePage() {
  const navigate = useNavigate()
  const [demoLoading, setDemoLoading] = useState(false)
  const [demoLoaded, setDemoLoaded] = useState(false)

  const handleLoadDemo = async () => {
    setDemoLoading(true)
    try {
      await loadDemo()
      setDemoLoaded(true)
    } catch (e) {
      console.error('Demo load failed:', e)
    }
    setDemoLoading(false)
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-16 pt-8"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="w-20 h-20 mx-auto mb-6 bg-primary-600/20 rounded-3xl flex items-center justify-center border border-primary-500/30"
        >
          <Brain className="w-10 h-10 text-primary-400" />
        </motion.div>
        <h1 className="text-5xl font-extrabold text-white mb-4 tracking-tight">
          Change Impact Memory
        </h1>
        <p className="text-xl text-white/50 max-w-2xl mx-auto leading-relaxed">
          AI that reconstructs enterprise decision reasoning from fragmented evidence
          and preserves it as verified organizational memory.
        </p>

        {/* HITL Badge */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full"
        >
          <Shield className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-emerald-300">Human-in-the-Loop AI System</span>
        </motion.div>
      </motion.div>

      {/* Mode Cards */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {/* Card 1: Create Memory */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card-hover p-8 group cursor-pointer"
          onClick={() => navigate('/create')}
        >
          <div className="w-14 h-14 bg-primary-600/20 rounded-2xl flex items-center justify-center border border-primary-500/30 mb-6 group-hover:scale-110 transition-transform">
            <Upload className="w-7 h-7 text-primary-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Create Organizational Memory</h2>
          <ul className="space-y-2 text-white/50 text-sm mb-6">
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-primary-400" />
              Upload documents
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-primary-400" />
              AI reconstructs decision reasoning
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-primary-400" />
              Human validates and approves
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-primary-400" />
              Approved reasoning becomes permanent memory
            </li>
          </ul>
          <div className="flex items-center gap-2 text-primary-400 font-medium group-hover:gap-3 transition-all">
            Start <ArrowRight className="w-4 h-4" />
          </div>
        </motion.div>

        {/* Card 2: Query Knowledge */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card-hover p-8 group cursor-pointer"
          onClick={() => navigate('/query')}
        >
          <div className="w-14 h-14 bg-emerald-600/20 rounded-2xl flex items-center justify-center border border-emerald-500/30 mb-6 group-hover:scale-110 transition-transform">
            <MessageSquare className="w-7 h-7 text-emerald-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Ask Verified Knowledge</h2>
          <ul className="space-y-2 text-white/50 text-sm mb-6">
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              Ask questions about past decisions
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              Answers ONLY from approved memory
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              Never hallucinate or invent
            </li>
            <li className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              Full evidence citations
            </li>
          </ul>
          <div className="flex items-center gap-2 text-emerald-400 font-medium group-hover:gap-3 transition-all">
            Open Assistant <ArrowRight className="w-4 h-4" />
          </div>
        </motion.div>
      </div>

      {/* Demo Loader */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-center"
      >
        <div className="glass-card p-6 inline-block">
          <p className="text-sm text-white/40 mb-3">Try with demo data: Password → Passkeys Migration</p>
          <button
            onClick={handleLoadDemo}
            disabled={demoLoading || demoLoaded}
            className="btn-secondary text-sm disabled:opacity-50"
          >
            {demoLoading ? 'Loading...' : demoLoaded ? '✓ Demo Loaded' : 'Load Demo Scenario'}
          </button>
          {demoLoaded && (
            <p className="text-xs text-emerald-400 mt-2">
              Demo loaded! Go to Create Memory to view it.
            </p>
          )}
        </div>
      </motion.div>
    </div>
  )
}
