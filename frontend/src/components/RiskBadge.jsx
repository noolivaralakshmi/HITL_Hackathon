import { AlertTriangle, Shield, ShieldAlert, Ban } from 'lucide-react'

const riskConfig = {
  LOW: { class: 'badge-low', icon: Shield, label: 'Low Risk' },
  MEDIUM: { class: 'badge-medium', icon: AlertTriangle, label: 'Medium Risk' },
  HIGH: { class: 'badge-high', icon: ShieldAlert, label: 'High Risk' },
  BLOCKED: { class: 'badge-blocked', icon: Ban, label: 'Blocked' },
}

export default function RiskBadge({ level }) {
  const config = riskConfig[level] || riskConfig.MEDIUM
  const Icon = config.icon

  return (
    <span className={config.class}>
      <Icon className="w-3 h-3 mr-1" />
      {config.label}
    </span>
  )
}
