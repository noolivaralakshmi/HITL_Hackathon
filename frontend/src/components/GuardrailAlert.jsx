import { motion } from 'framer-motion'
import { AlertTriangle, ShieldAlert, Ban, Info } from 'lucide-react'

const severityConfig = {
  warning: { icon: AlertTriangle, color: 'border-amber-500/30 bg-amber-500/10 text-amber-300' },
  critical: { icon: ShieldAlert, color: 'border-red-500/30 bg-red-500/10 text-red-300' },
  blocked: { icon: Ban, color: 'border-red-700/50 bg-red-900/20 text-red-200' },
  info: { icon: Info, color: 'border-blue-500/30 bg-blue-500/10 text-blue-300' },
}

export default function GuardrailAlert({ flags }) {
  if (!flags || flags.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="space-y-2"
    >
      <h4 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
        Guardrail Checks
      </h4>
      {flags.map((flag, idx) => {
        const config = severityConfig[flag.severity] || severityConfig.warning
        const Icon = config.icon
        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`flex items-start gap-3 p-3 rounded-xl border ${config.color}`}
          >
            <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm">{flag.message}</p>
              {flag.field && (
                <p className="text-xs opacity-60 mt-1">Field: {flag.field}</p>
              )}
            </div>
            <span className="text-xs uppercase font-medium opacity-60">{flag.type}</span>
          </motion.div>
        )
      })}
    </motion.div>
  )
}
