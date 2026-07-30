import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Edit3, Lock, RotateCcw } from 'lucide-react'
import { useUser } from '../context/UserContext'
import RiskBadge from './RiskBadge'
import StatusChip from './StatusChip'

const ROLE_HIERARCHY = { viewer: 0, reviewer: 1, approver: 2, admin: 3 }
const REQUIRED_ROLES = { LOW: 'reviewer', MEDIUM: 'approver', HIGH: 'admin', BLOCKED: null }

export default function ApprovalBar({ memory, onApprove, onReject, onEdit, onRollback }) {
  const { currentUser } = useUser()
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showRollbackModal, setShowRollbackModal] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [rollbackReason, setRollbackReason] = useState('')

  const riskLevel = memory?.risk_level || 'MEDIUM'
  const status = memory?.status || 'DRAFT'
  const isBlocked = riskLevel === 'BLOCKED'
  const requiredRole = REQUIRED_ROLES[riskLevel]
  const canApprove = !isBlocked && ROLE_HIERARCHY[currentUser.role] >= ROLE_HIERARCHY[requiredRole]
  const canEdit = ROLE_HIERARCHY[currentUser.role] >= ROLE_HIERARCHY.reviewer
  const canRollback = ROLE_HIERARCHY[currentUser.role] >= ROLE_HIERARCHY.admin && status === 'VERIFIED'

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
          <RiskBadge level={riskLevel} />
        </div>
        {!canApprove && status === 'DRAFT' && !isBlocked && (
          <div className="flex items-center gap-2 text-sm text-amber-300/70">
            <Lock className="w-4 h-4" />
            Requires {requiredRole} role to approve
          </div>
        )}
        {isBlocked && (
          <div className="flex items-center gap-2 text-sm text-red-300/70">
            <Lock className="w-4 h-4" />
            Blocked by guardrail checks
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {status === 'DRAFT' && (
        <div className="flex items-center gap-3">
          <button
            onClick={onApprove}
            disabled={!canApprove}
            className="btn-success flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <CheckCircle className="w-4 h-4" />
            Approve
          </button>

          <button
            onClick={onEdit}
            disabled={!canEdit}
            className="btn-secondary flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Edit3 className="w-4 h-4" />
            Edit
          </button>

          <button
            onClick={() => setShowRejectModal(true)}
            disabled={!canEdit}
            className="btn-danger flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
        </div>
      )}

      {status === 'VERIFIED' && canRollback && (
        <button
          onClick={() => setShowRollbackModal(true)}
          className="btn-secondary flex items-center gap-2 border-orange-500/30 text-orange-300 hover:bg-orange-500/10"
        >
          <RotateCcw className="w-4 h-4" />
          Rollback
        </button>
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
            <p className="text-sm text-white/50 mb-4">
              This will revert the memory to draft status and remove it from verified knowledge.
            </p>
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
