import { Shield, CheckCircle, XCircle, RotateCcw, Ban, Clock, Trash2 } from 'lucide-react'

const statusConfig = {
  DRAFT: { class: 'status-draft', icon: Shield, label: 'Draft' },
  PENDING_REVIEW: { class: 'badge-medium', icon: Clock, label: 'Pending Review' },
  VERIFIED: { class: 'status-verified', icon: CheckCircle, label: 'Verified' },
  REJECTED: { class: 'status-rejected', icon: XCircle, label: 'Rejected' },
  ROLLED_BACK: { class: 'status-rolled-back', icon: RotateCcw, label: 'Rolled Back' },
  BLOCKED: { class: 'badge-blocked', icon: Ban, label: 'Blocked' },
  DISCARDED: { class: 'badge bg-gray-500/20 text-gray-300 border border-gray-500/30', icon: Trash2, label: 'Discarded' },
}

export default function StatusChip({ status }) {
  const config = statusConfig[status] || statusConfig.DRAFT
  const Icon = config.icon

  return (
    <span className={config.class}>
      <Icon className="w-3 h-3 mr-1" />
      {config.label}
    </span>
  )
}
