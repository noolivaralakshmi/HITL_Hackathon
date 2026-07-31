import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Target, Lightbulb, XCircle, AlertTriangle, Puzzle, FileText, Users, Calendar, ExternalLink } from 'lucide-react'
import api from '../api/client'

function EvidenceLink({ document, memoryId }) {
  const [url, setUrl] = useState(null)

  useEffect(() => {
    if (memoryId) {
      api.get(`/documents/memory/${memoryId}`)
        .then(res => {
          const docs = res.data?.documents || []
          const match = docs.find(d =>
            d.filename === document ||
            d.filename.toLowerCase().includes(document.toLowerCase().replace('.pdf', '').replace('.txt', ''))
          )
          if (match?.download_url) setUrl(match.download_url)
        })
        .catch(() => {})
    }
  }, [document, memoryId])

  if (url) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer"
        className="text-sm font-medium text-blue-400 hover:text-blue-300 underline underline-offset-2 flex items-center gap-1">
        {document} <ExternalLink className="w-3 h-3" />
      </a>
    )
  }
  return <p className="text-sm font-medium text-white">{document}</p>
}

const sectionIcons = {
  what_changed: ArrowRight,
  business_objective: Target,
  technical_objective: Lightbulb,
  alternatives_considered: XCircle,
  risks_accepted: AlertTriangle,
  assumptions: Puzzle,
  evidence: FileText,
  decision_makers: Users,
  timeline: Calendar,
  rollback_strategy: ArrowRight,
  risk_owners: Users,
  success_criteria: Target,
  communication_plan: FileText,
  dependencies: Puzzle,
}

export default function ReasoningRecord({ reasoning, memoryId }) {
  if (!reasoning || Object.keys(reasoning).length === 0) return null

  const renderSection = (key, value, idx) => {
    const Icon = sectionIcons[key] || FileText
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())

    return (
      <motion.div
        key={key}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: idx * 0.05 }}
        className="p-4 bg-white/5 rounded-xl border border-white/10"
      >
        <div className="flex items-center gap-2 mb-3">
          <Icon className="w-4 h-4 text-primary-400" />
          <h4 className="text-sm font-semibold text-white/80 uppercase tracking-wider">{label}</h4>
        </div>

        {renderValue(key, value)}
      </motion.div>
    )
  }

  const renderValue = (key, value) => {
    if (key === 'alternatives_considered' && Array.isArray(value)) {
      return (
        <div className="space-y-2">
          {value.map((alt, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
              <XCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-white">{alt.name}</p>
                <p className="text-xs text-red-300/70 mt-0.5">Rejected: {alt.rejected_reason}</p>
              </div>
            </div>
          ))}
        </div>
      )
    }

    if (key === 'evidence' && Array.isArray(value)) {
      return (
        <div className="space-y-2">
          {value.map((ev, i) => (
            <div key={i} className="flex items-start gap-3 p-2 bg-white/5 rounded-lg">
              <FileText className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <EvidenceLink document={ev.document} memoryId={memoryId} />
                <p className="text-xs text-white/50">{ev.supports}</p>
              </div>
            </div>
          ))}
        </div>
      )
    }

    if (Array.isArray(value)) {
      return (
        <ul className="space-y-1.5">
          {value.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-white/80">
              <span className="text-white/30 mt-0.5">•</span>
              <span>{typeof item === 'string' ? item : JSON.stringify(item)}</span>
            </li>
          ))}
        </ul>
      )
    }

    return <p className="text-sm text-white/80 leading-relaxed">{String(value)}</p>
  }

  const sections = Object.entries(reasoning).filter(([_, v]) => v && (Array.isArray(v) ? v.length > 0 : true))

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <h3 className="text-lg font-semibold text-white flex items-center gap-2">
        <FileText className="w-5 h-5 text-primary-400" />
        Reasoning Record
      </h3>
      <div className="grid gap-4 lg:grid-cols-2">
        {sections.map(([key, value], idx) => renderSection(key, value, idx))}
      </div>
    </motion.div>
  )
}
