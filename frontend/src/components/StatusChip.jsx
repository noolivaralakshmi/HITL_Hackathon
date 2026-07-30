import { Shield, CheckCircle, XCircle, RotateCcw, Ban } from 'lucide-react'

const statusConfig = {
  DRAFT: { class: 'status-draft', icon: Shield, label: 'Draft' },
  VERIFIED: { class: 'status-verified', icon: CheckCircle, label: 'Verified' },
  REJECTED: { class: 'status-rejected', icon: XCircle, label: 'Rejected' },
  ROLLED_BACK: { class: 'status-rolled-back', icon: RotateCcw, label: 'Rolled Back' },
  BLOCKED: { class: 'badge-blocked', icon: Ban, label: 'Blocked' },
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
