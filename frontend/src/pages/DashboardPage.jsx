import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import { FileText, Clock, CheckCircle, XCircle, Bell, ArrowRight } from 'lucide-react'
import api from '../api/client'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { currentUser, isReviewer } = useUser()
  const [dashboard, setDashboard] = useState(null)
  const [activeTab, setActiveTab] = useState('contributed')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (currentUser) {
      api.get(`/users/${currentUser.id}/dashboard`)
        .then(res => setDashboard(res.data))
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [currentUser])

  const handleSendReminder = async (memoryId) => {
    try {
      await api.post(`/memory/${memoryId}/send-reminder`, { user_id: currentUser.id })
      alert('Reminder sent to reviewer!')
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to send reminder')
    }
  }

  const tabs = [
    { id: 'contributed', label: 'My Contributions', icon: FileText, count: dashboard?.tabs?.contributed?.length || 0 },
    ...(isReviewer ? [
      { id: 'pending_review', label: 'Pending Review', icon: Clock, count: dashboard?.tabs?.pending_review?.length || 0 },
      { id: 'approved', label: 'Approved', icon: CheckCircle, count: dashboard?.tabs?.approved?.length || 0 },
      { id: 'rejected', label: 'Rejected', icon: XCircle, count: dashboard?.tabs?.rejected?.length || 0 },
    ] : []),
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'VERIFIED': return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
      case 'PENDING_REVIEW': return 'bg-amber-500/20 text-amber-300 border-amber-500/30'
      case 'DRAFT': return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      case 'REJECTED': return 'bg-red-500/20 text-red-300 border-red-500/30'
      case 'DISCARDED': return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  const renderMemoryCard = (mem, showReviewer = true, showContributor = false, showReminder = false) => (
    <motion.div
      key={mem.id}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 hover:bg-white/10 transition-all cursor-pointer"
      onClick={() => navigate(`/memory/${mem.id}`)}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-white font-semibold">{mem.change_type || 'Untitled'}</h3>
        <span className={`text-xs px-2.5 py-1 rounded-full border ${getStatusColor(mem.status)}`}>
          {mem.status === 'PENDING_REVIEW' ? 'Pending Review' : mem.status}
        </span>
      </div>

      <div className="flex items-center gap-4 text-sm text-white/50">
        <span>Confidence: {mem.confidence}%</span>
        {mem.risk_level && <span>Risk: {mem.risk_level}</span>}
        <span>{new Date(mem.created_at).toLocaleDateString()}</span>
      </div>

      {showReviewer && mem.reviewer_name && (
        <p className="text-xs text-white/40 mt-2">Reviewer: {mem.reviewer_name}</p>
      )}
      {showReviewer && mem.assigned_reviewer && !mem.reviewer_name && (
        <p className="text-xs text-white/40 mt-2">Assigned to reviewer</p>
      )}
      {showContributor && mem.contributor_name && (
        <p className="text-xs text-white/40 mt-2">Submitted by: {mem.contributor_name}</p>
      )}

      {showReminder && mem.status === 'PENDING_REVIEW' && (
        <button
          onClick={(e) => { e.stopPropagation(); handleSendReminder(mem.id) }}
          className="mt-3 text-xs flex items-center gap-1 text-amber-400 hover:text-amber-300 bg-amber-500/10 px-3 py-1.5 rounded-lg border border-amber-500/20 hover:border-amber-500/30 transition-all"
        >
          <Bell className="w-3 h-3" /> Send Reminder
        </button>
      )}
    </motion.div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }

  const currentItems = dashboard?.tabs?.[activeTab] || []

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-white/40">Welcome back, {currentUser?.name}</p>
        </div>
        <button
          onClick={() => navigate('/create')}
          className="btn-primary flex items-center gap-2"
        >
          Create Memory <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-primary-600/20 border border-primary-500/30 text-primary-300'
                  : 'bg-white/5 border border-white/10 text-white/50 hover:text-white hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
              {tab.count > 0 && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                  activeTab === tab.id ? 'bg-primary-500/30' : 'bg-white/10'
                }`}>{tab.count}</span>
              )}
            </button>
          )
        })}
      </div>

      {/* Content */}
      <div className="space-y-4">
        {currentItems.length === 0 ? (
          <div className="text-center py-16 text-white/30">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-40" />
            <p className="text-lg">No items in this tab</p>
            {activeTab === 'contributed' && (
              <button onClick={() => navigate('/create')} className="btn-secondary text-sm mt-4">
                Create Your First Memory
              </button>
            )}
          </div>
        ) : (
          currentItems.map((mem) =>
            renderMemoryCard(
              mem,
              activeTab === 'contributed',
              activeTab !== 'contributed',
              activeTab === 'contributed' && mem.status === 'PENDING_REVIEW'
            )
          )
        )}
      </div>
    </div>
  )
}
