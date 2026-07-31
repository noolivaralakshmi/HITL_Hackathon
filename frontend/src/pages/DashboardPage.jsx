import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import { FileText, Clock, CheckCircle, XCircle, Bell, ArrowRight, Brain, TrendingUp, Shield, Activity } from 'lucide-react'
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
    { id: 'contributed', label: 'My Contributions', icon: FileText },
    ...(isReviewer ? [
      { id: 'pending_review', label: 'Pending Review', icon: Clock },
      { id: 'approved', label: 'Approved', icon: CheckCircle },
      { id: 'rejected', label: 'Rejected', icon: XCircle },
    ] : []),
  ]

  const getCount = (tabId) => dashboard?.tabs?.[tabId]?.length || 0

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
      className="group bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-white/[0.12] rounded-xl p-5 transition-all duration-200 cursor-pointer"
      onClick={() => navigate(`/memory/${mem.id}`)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-600/10 border border-primary-500/20 flex items-center justify-center">
            <Brain className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold group-hover:text-primary-300 transition-colors">{mem.change_type || 'Untitled'}</h3>
            <p className="text-xs text-white/40">{new Date(mem.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
          </div>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full border ${getStatusColor(mem.status)}`}>
          {mem.status === 'PENDING_REVIEW' ? 'Pending Review' : mem.status}
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs text-white/40 ml-[52px]">
        <span className="flex items-center gap-1">
          <TrendingUp className="w-3 h-3" /> {mem.confidence}% confidence
        </span>
        {mem.risk_level && (
          <span className={`flex items-center gap-1 ${
            mem.risk_level === 'LOW' ? 'text-emerald-400' :
            mem.risk_level === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'
          }`}>
            <Shield className="w-3 h-3" /> {mem.risk_level}
          </span>
        )}
      </div>

      {showReviewer && mem.reviewer_name && (
        <p className="text-xs text-white/30 mt-3 ml-[52px]">Reviewer: {mem.reviewer_name}</p>
      )}
      {showContributor && mem.contributor_name && (
        <p className="text-xs text-white/30 mt-3 ml-[52px]">Submitted by: {mem.contributor_name}</p>
      )}

      {showReminder && mem.status === 'PENDING_REVIEW' && (
        <div className="mt-3 ml-[52px]">
          <button
            onClick={(e) => { e.stopPropagation(); handleSendReminder(mem.id) }}
            className="text-xs flex items-center gap-1.5 text-amber-400 hover:text-amber-300 bg-amber-500/10 px-3 py-1.5 rounded-lg border border-amber-500/20 hover:border-amber-500/30 transition-all"
          >
            <Bell className="w-3 h-3" /> Send Reminder to Reviewer
          </button>
        </div>
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

  const totalContributions = getCount('contributed')
  const pendingCount = getCount('pending_review')
  const approvedCount = getCount('approved')
  const currentItems = dashboard?.tabs?.[activeTab] || []

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-white/40 mt-1">Welcome back, {currentUser?.name}</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className={`grid gap-4 mb-8 ${isReviewer ? 'grid-cols-2 md:grid-cols-4' : 'grid-cols-1 md:grid-cols-2'}`}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-primary-600/10 to-primary-600/5 border border-primary-500/20 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Total Contributions</p>
              <p className="text-3xl font-bold text-white mt-1">{totalContributions}</p>
            </div>
            <div className="w-12 h-12 bg-primary-600/20 rounded-xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-primary-400" />
            </div>
          </div>
        </motion.div>

        {isReviewer && (
          <>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-amber-600/10 to-amber-600/5 border border-amber-500/20 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Pending Review</p>
                  <p className="text-3xl font-bold text-white mt-1">{pendingCount}</p>
                </div>
                <div className="w-12 h-12 bg-amber-600/20 rounded-xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-amber-400" />
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="bg-gradient-to-br from-emerald-600/10 to-emerald-600/5 border border-emerald-500/20 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Approved</p>
                  <p className="text-3xl font-bold text-white mt-1">{approvedCount}</p>
                </div>
                <div className="w-12 h-12 bg-emerald-600/20 rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-emerald-400" />
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
              className="bg-gradient-to-br from-violet-600/10 to-violet-600/5 border border-violet-500/20 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Verified Knowledge</p>
                  <p className="text-3xl font-bold text-white mt-1">{approvedCount}</p>
                </div>
                <div className="w-12 h-12 bg-violet-600/20 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6 text-violet-400" />
                </div>
              </div>
            </motion.div>
          </>
        )}

        {!isReviewer && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-amber-600/10 to-amber-600/5 border border-amber-500/20 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-white/40 uppercase tracking-wider font-medium">Awaiting Review</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {(dashboard?.tabs?.contributed || []).filter(m => m.status === 'PENDING_REVIEW').length}
                </p>
              </div>
              <div className="w-12 h-12 bg-amber-600/20 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-amber-400" />
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-white/[0.06] mb-6">
        <div className="flex items-center gap-0">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const count = getCount(tab.id)
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center gap-2 px-5 py-3.5 text-sm font-medium transition-all border-b-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-white'
                    : 'border-transparent text-white/40 hover:text-white/70 hover:border-white/20'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {count > 0 && (
                  <span className={`text-xs px-1.5 py-0.5 rounded-full min-w-[20px] text-center ${
                    activeTab === tab.id ? 'bg-primary-500/30 text-primary-300' : 'bg-white/10 text-white/50'
                  }`}>{count}</span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        {currentItems.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10">
              <FileText className="w-8 h-8 text-white/20" />
            </div>
            <p className="text-lg text-white/30 font-medium">No items yet</p>
            <p className="text-sm text-white/20 mt-1">
              {activeTab === 'contributed' ? 'Create your first organizational memory to get started.' :
               activeTab === 'pending_review' ? 'No memories are waiting for your review.' :
               activeTab === 'approved' ? "You haven't approved any memories yet." :
               "No rejected memories."}
            </p>
            {activeTab === 'contributed' && (
              <button onClick={() => navigate('/create')} className="btn-primary text-sm mt-6">
                Create Your First Memory
              </button>
            )}
          </motion.div>
        ) : (
          currentItems.map((mem, idx) => (
            <motion.div key={mem.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
              {renderMemoryCard(
                mem,
                activeTab === 'contributed',
                activeTab !== 'contributed',
                activeTab === 'contributed' && mem.status === 'PENDING_REVIEW'
              )}
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}
