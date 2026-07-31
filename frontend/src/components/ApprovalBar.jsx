import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Edit3, Send, RotateCcw, UserCheck } from 'lucide-react'
import { useUser } from '../context/UserContext'
import RiskBadge from './RiskBadge'
import StatusChip from './StatusChip'
import api from '../api/client'

export default function ApprovalBar({ memory, onApprove, onReject, onEdit, onDiscard, onSubmitForReview, onRollback }) {
  const { currentUser, isReviewer } = useUser()
  const [reviewers, setReviewers] = useState([])
  const [selectedReviewer, setSelectedReviewer] = useState('')
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [showRollbackModal, setShowRollbackModal] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [rollbackReason, setRollbackReason] = useState('')

  const status = memory?.status || 'DRAFT'
  const isContributor = memory?.contributor_id === currentUser?.id
  const isAssignedReviewer = memory?.assigned_reviewer === currentUser?.id

  useEffect(() => {
    api.get('/users/reviewers').then(res => {
      setReviewers(res.data?.reviewers || [])
      if (res.data?.reviewers?.length > 0) {
        setSelectedReviewer(res.data.reviewers[0].id)
      }
    }).catch(() => {})
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      {/* Status + Risk Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <StatusChip status={status} />
          <RiskBadge level={memory?.risk_level || 'MEDIUM'} />
        </div>
      </div>

      {/* DRAFT - Contributor actions: Edit / Discard / Send for Approval */}
      {status === 'DRAFT' && isContributor && (
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={onEdit}
            className="btn-secondary flex items-center gap-2"
          >
            <Edit3 className="w-4 h-4" /> Edit
          </button>

          <button
            onClick={onDiscard}
            className="btn-danger flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" /> Discard
          </button>

          <button
            onClick={() => setShowSubmitModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Send className="w-4 h-4" /> Send for Approval
          </button>
        </div>
      )}

      {/* PENDING_REVIEW - Reviewer actions: Approve / Reject */}
      {status === 'PENDING_REVIEW' && isAssignedReviewer && (
        <div className="flex items-center gap-3">
          <button
            onClick={onApprove}
            className="btn-success flex items-center gap-2"
          >
            <CheckCircle className="w-4 h-4" /> Approve
          </button>

          <button
            onClick={() => setShowRejectModal(true)}
            className="btn-danger flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" /> Reject
          </button>

          <button
            onClick={onEdit}
            className="btn-secondary flex items-center gap-2"
          >
            <Edit3 className="w-4 h-4" /> Edit
          </button>
        </div>
      )}

      {/* PENDING_REVIEW - shown to contributor (read only) */}
      {status === 'PENDING_REVIEW' && isContributor && !isAssignedReviewer && (
        <div className="flex items-center gap-2 text-amber-300/70 text-sm">
          <UserCheck className="w-4 h-4" />
          Waiting for reviewer approval
        </div>
      )}

      {/* VERIFIED - Rollback (reviewer only) */}
      {status === 'VERIFIED' && isReviewer && (
        <button
          onClick={() => setShowRollbackModal(true)}
          className="btn-secondary flex items-center gap-2 border-orange-500/30 text-orange-300 hover:bg-orange-500/10"
        >
          <RotateCcw className="w-4 h-4" /> Rollback
        </button>
      )}

      {/* Submit for Review Modal */}
      {showSubmitModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowSubmitModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="glass-card p-6 w-full max-w-md mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-white mb-4">Send for Approval</h3>
            <div className="mb-4">
              <label className="text-sm text-white/60 block mb-2">Select Reviewer</label>
              <select
                value={selectedReviewer}
                onChange={(e) => setSelectedReviewer(e.target.value)}
                className="input-field"
              >
                {reviewers.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowSubmitModal(false)} className="btn-secondary text-sm px-4 py-2">
                Cancel
              </button>
              <button
                onClick={() => {
                  onSubmitForReview(selectedReviewer)
                  setShowSubmitModal(false)
                }}
                disabled={!selectedReviewer}
                className="btn-primary text-sm px-4 py-2 disabled:opacity-30"
              >
                Submit
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowRejectModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="glass-card p-6 w-full max-w-md mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-white mb-4">Reject Memory</h3>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection..."
              className="input-field h-24 resize-none mb-4"
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowRejectModal(false)} className="btn-secondary text-sm px-4 py-2">
                Cancel
              </button>
              <button
                onClick={() => { onReject(rejectReason); setShowRejectModal(false) }}
                disabled={!rejectReason.trim()}
                className="btn-danger text-sm px-4 py-2 disabled:opacity-30"
              >
                Reject
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Rollback Modal */}
      {showRollbackModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowRollbackModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="glass-card p-6 w-full max-w-md mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-white mb-2">Rollback Memory</h3>
            <p className="text-sm text-white/50 mb-4">This will revert to draft and remove from verified knowledge.</p>
            <textarea
              value={rollbackReason}
              onChange={(e) => setRollbackReason(e.target.value)}
              placeholder="Reason for rollback..."
              className="input-field h-24 resize-none mb-4"
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowRollbackModal(false)} className="btn-secondary text-sm px-4 py-2">
                Cancel
              </button>
              <button
                onClick={() => { onRollback(rollbackReason); setShowRollbackModal(false) }}
                disabled={!rollbackReason.trim()}
                className="btn-danger text-sm px-4 py-2 disabled:opacity-30"
              >
                Confirm Rollback
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  )
}
