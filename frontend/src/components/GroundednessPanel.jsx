import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle, FileText, RefreshCw } from 'lucide-react'
import api from '../api/client'

/**
 * Displays groundedness verification results — shows how well AI reasoning
 * is grounded in the source documents, with citations for each claim.
 */
export default function GroundednessPanel({ groundedness, memoryId, onUpdate }) {
  const [isVerifying, setIsVerifying] = useState(false)
  const [expanded, setExpanded] = useState(false)

  if (!groundedness || !groundedness.claims || groundedness.claims.length === 0) {
    return (
      <div className="glass-card p-5 border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white/40" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white/60">Groundedness Verification</h4>
              <p className="text-xs text-white/30">Not yet verified against source documents</p>
            </div>
          </div>
          {memoryId && (
            <button
              onClick={handleReVerify}
              disabled={isVerifying}
              className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3 h-3 ${isVerifying ? 'animate-spin' : ''}`} />
              {isVerifying ? 'Verifying...' : 'Verify Now'}
            </button>
          )}
        </div>
      </div>
    )
  }

  const score = groundedness.groundedness_score || {}
  const percentage = score.percentage || 0
  const claims = groundedness.claims || []
  const criticalGaps = groundedness.critical_gaps || []

  const scoreColor = percentage >= 80 ? 'emerald' : percentage >= 60 ? 'amber' : 'red'
  const scoreLabel = percentage >= 80 ? 'Well Grounded' : percentage >= 60 ? 'Partially Grounded' : 'Poorly Grounded'

  async function handleReVerify() {
    if (!memoryId) return
    setIsVerifying(true)
    try {
      const res = await api.post(`/memory/${memoryId}/verify-groundedness`)
      if (onUpdate) onUpdate(res.data.groundedness)
    } catch (e) {
      console.error('Groundedness verification failed:', e)
    }
    setIsVerifying(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card p-5 border-${scoreColor}-500/20 bg-${scoreColor}-500/5`}
    >
      {/* Header with score */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 bg-${scoreColor}-500/20 rounded-xl flex items-center justify-center`}>
            {percentage >= 80 ? (
              <CheckCircle className={`w-5 h-5 text-${scoreColor}-400`} />
            ) : percentage >= 60 ? (
              <AlertTriangle className={`w-5 h-5 text-${scoreColor}-400`} />
            ) : (
              <XCircle className={`w-5 h-5 text-${scoreColor}-400`} />
            )}
          </div>
          <div>
            <h4 className={`text-sm font-semibold text-${scoreColor}-300`}>
              Groundedness: {percentage}% — {scoreLabel}
            </h4>
            <p className="text-xs text-white/40">
              {score.supported} supported · {score.partially_supported} partial · {score.unsupported} unsupported of {score.total} claims
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {memoryId && (
            <button
              onClick={handleReVerify}
              disabled={isVerifying}
              className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3 h-3 ${isVerifying ? 'animate-spin' : ''}`} />
              Re-verify
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-white/40 hover:text-white/60 transition-colors"
          >
            {expanded ? 'Collapse' : 'Show Details'}
          </button>
        </div>
      </div>

      {/* Summary */}
      {groundedness.summary && (
        <p className="text-sm text-white/60 mb-3">{groundedness.summary}</p>
      )}

      {/* Critical gaps warning */}
      {criticalGaps.length > 0 && (
        <div className="mb-3 p-3 bg-red-500/10 rounded-lg border border-red-500/20">
          <p className="text-xs font-semibold text-red-300 mb-1">Unsupported Claims (requires reviewer attention):</p>
          <ul className="space-y-1">
            {criticalGaps.map((gap, idx) => (
              <li key={idx} className="text-xs text-red-200/70 flex items-start gap-2">
                <XCircle className="w-3 h-3 mt-0.5 shrink-0" />
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Detailed claims (expandable) */}
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="space-y-2 mt-3 max-h-96 overflow-y-auto"
        >
          {claims.map((claim, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border ${
                claim.status === 'SUPPORTED' ? 'bg-emerald-500/5 border-emerald-500/15' :
                claim.status === 'PARTIALLY_SUPPORTED' ? 'bg-amber-500/5 border-amber-500/15' :
                'bg-red-500/5 border-red-500/15'
              }`}
            >
              <div className="flex items-start gap-2">
                {claim.status === 'SUPPORTED' ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                ) : claim.status === 'PARTIALLY_SUPPORTED' ? (
                  <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-white/80">{claim.claim}</p>
                  <p className="text-xs text-white/30 mt-0.5">Field: {claim.field}</p>
                  {claim.source_document && (
                    <p className="text-xs text-white/50 mt-1">
                      <span className="text-white/30">Source:</span> {claim.source_document}
                    </p>
                  )}
                  {claim.source_quote && (
                    <p className="text-xs text-white/40 mt-1 italic border-l-2 border-white/10 pl-2">
                      "{claim.source_quote}"
                    </p>
                  )}
                  {claim.explanation && (
                    <p className="text-xs text-white/30 mt-1">{claim.explanation}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  )
}
