import { motion } from 'framer-motion'
import { AlertTriangle } from 'lucide-react'

export default function MissingInfo({ items }) {
  if (!items || items.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 border-amber-500/20"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center border border-amber-500/30">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Missing Information Detected</h3>
          <p className="text-sm text-white/50">{items.length} gap{items.length > 1 ? 's' : ''} identified</p>
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center gap-3 p-3 bg-amber-500/5 rounded-xl border border-amber-500/10"
          >
            <span className="text-amber-400">⚠</span>
            <span className="text-sm text-white/80">
              {item.replace(/^⚠\s*/, '')}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
