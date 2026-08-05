export default function ConfidenceBadge({ confidence }) {
  const getColor = () => {
    if (confidence >= 80) return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30'
    if (confidence >= 60) return 'text-amber-400 bg-amber-500/20 border-amber-500/30'
    return 'text-red-400 bg-red-500/20 border-red-500/30'
  }

  return (
    <span className={`badge border ${getColor()}`}>
      <svg className="w-3 h-3 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
      {confidence}% confidence
    </span>
  )
}
