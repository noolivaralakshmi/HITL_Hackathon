import { motion } from 'framer-motion'
import { Clock, Upload, Bot, User, CheckCircle, XCircle, Edit3, RotateCcw, ShieldAlert, Ban } from 'lucide-react'

const actionConfig = {
  USER_REQUEST: { icon: Upload, color: 'bg-blue-500', label: 'User Request' },
  AI_DRAFT: { icon: Bot, color: 'bg-purple-500', label: 'AI Draft Generated' },
  HUMAN_REVIEW: { icon: User, color: 'bg-emerald-500', label: 'Human Review' },
  APPROVED: { icon: CheckCircle, color: 'bg-emerald-500', label: 'Approved' },
  REJECTED: { icon: XCircle, color: 'bg-red-500', label: 'Rejected' },
  EDITED: { icon: Edit3, color: 'bg-amber-500', label: 'Edited' },
  ROLLED_BACK: { icon: RotateCcw, color: 'bg-orange-500', label: 'Rolled Back' },
  GUARDRAIL_FLAG: { icon: ShieldAlert, color: 'bg-amber-500', label: 'Guardrail Flag' },
  BLOCKED: { icon: Ban, color: 'bg-red-700', label: 'Blocked' },
}

export default function AuditTimeline({ entries }) {
  if (!entries || entries.length === 0) {
    return (
      <div className="text-center py-8 text-white/30 text-sm">
        No audit history yet.
      </div>
    )
  }

  return (
    <div className="space-y-1">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4 flex items-center gap-2">
        <Clock className="w-4 h-4" />
        Action Log
      </h3>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-white/10" />

        {entries.map((entry, idx) => {
          const config = actionConfig[entry.action] || actionConfig.USER_REQUEST
          const Icon = config.icon
          const time = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : ''

          return (
            <motion.div
              key={entry.id || idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="relative pl-10 pb-6 last:pb-0"
            >
              {/* Dot */}
              <div className={`absolute left-2.5 w-3 h-3 rounded-full ${config.color} ring-4 ring-surface-950`} />

              {/* Content */}
              <div className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-white/10 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-white/60" />
                    <span className="text-sm font-medium text-white">{config.label}</span>
                  </div>
                  <span className="text-xs text-white/30">{time}</span>
                </div>

                {entry.user_name && (
                  <p className="text-xs text-white/40 mb-1">By: {entry.user_name} ({entry.user_role})</p>
                )}

                {entry.human_decision && (
                  <p className="text-xs text-white/60 mt-1">"{entry.human_decision}"</p>
                )}

                {entry.risk_level && (
                  <span className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full ${
                    entry.risk_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-300' :
                    entry.risk_level === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                    'bg-red-500/20 text-red-300'
                  }`}>
                    {entry.risk_level} risk
                  </span>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
