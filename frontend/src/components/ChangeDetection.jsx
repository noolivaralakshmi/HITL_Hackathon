import { motion } from 'framer-motion'
import { CheckCircle, Sparkles } from 'lucide-react'
import ConfidenceBadge from './ConfidenceBadge'
import RiskBadge from './RiskBadge'

export default function ChangeDetection({ changeType, confidence, detectionReasons, riskLevel }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 space-y-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600/20 rounded-xl flex items-center justify-center border border-primary-500/30">
            <Sparkles className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
            <p className="text-sm text-white/50">Detected Change Type</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ConfidenceBadge confidence={confidence} />
          <RiskBadge level={riskLevel} />
        </div>
      </div>

      {/* Change Type */}
      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
        <p className="text-2xl font-bold text-white">{changeType}</p>
        <p className="text-sm text-white/40 mt-1">Change Classification</p>
      </div>

      {/* Detection Reasons */}
      <div>
        <p className="text-sm font-medium text-white/60 mb-2">Why detected:</p>
        <div className="space-y-2">
          {detectionReasons.map((reason, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span className="text-sm text-white/80">{reason}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
