import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Check, Upload as UploadIcon, Sparkles, MessageSquare, FileCheck, Send } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import {
  uploadDocuments, generateMemory, getMemory, listMemories,
  approveMemory, rejectMemory, editMemoryReasoning, rollbackMemory,
  sendChatMessage, getChatHistory, getAuditLog, addDocumentsToMemory,
  getDocumentsByMemory
} from '../api/client'
import api from '../api/client'

import FileUpload from '../components/FileUpload'
import ChangeDetection from '../components/ChangeDetection'
import ReasoningRecord from '../components/ReasoningRecord'
import EditableReasoningRecord from '../components/EditableReasoningRecord'
import MissingInfo from '../components/MissingInfo'
import ChatPanel from '../components/ChatPanel'
import ApprovalBar from '../components/ApprovalBar'
import AuditTimeline from '../components/AuditTimeline'
import GuardrailAlert from '../components/GuardrailAlert'

const STEPS = [
  { id: 1, label: 'Upload', icon: UploadIcon },
  { id: 2, label: 'Analysis', icon: Sparkles },
  { id: 3, label: 'Review', icon: MessageSquare },
  { id: 4, label: 'Complete', icon: FileCheck },
]

export default function CreateMemoryPage() {
  const navigate = useNavigate()
  const { memoryId } = useParams()
  const { currentUser, isReviewer } = useUser()
  const [step, setStep] = useState(1)
  const [files, setFiles] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [memory, setMemory] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)
  const [auditLog, setAuditLog] = useState([])
  const [duplicateWarning, setDuplicateWarning] = useState(null)
  const [piiWarnings, setPiiWarnings] = useState([])
  const [isEditing, setIsEditing] = useState(false)

  // Load existing memory if viewing one from dashboard
  useEffect(() => {
    if (memoryId) {
      getMemory(memoryId).then(res => {
        setMemory(res.data)
        setStep(3)
        loadAuditLog(memoryId)
        loadChatHistory(memoryId)
      }).catch(() => {})
    }
  }, [memoryId])

  const loadAuditLog = async (id) => {
    try {
      const res = await getAuditLog(id)
      setAuditLog(res.data?.log || [])
    } catch (e) {}
  }

  const loadChatHistory = async (id) => {
    try {
      const res = await getChatHistory(id)
      setChatMessages(res.data?.messages || [])
    } catch (e) {}
  }

  const handleGenerate = async () => {
    if (files.length === 0) return
    setIsLoading(true)
    setPiiWarnings([])

    try {
      const uploadRes = await uploadDocuments(files)
      const docIds = uploadRes.data.documents.map(d => d.id)

      if (uploadRes.data.pii_warnings) {
        setPiiWarnings(uploadRes.data.pii_warnings)
      }

      const genRes = await generateMemory(docIds, currentUser.id)
      setMemory(genRes.data)

      if (genRes.data.duplicate_warning) {
        setDuplicateWarning(genRes.data.duplicate_warning)
      }

      setStep(2)
      await loadAuditLog(genRes.data.id)
      setTimeout(() => setStep(3), 1500)
    } catch (e) {
      console.error('Error generating memory:', e)
    }
    setIsLoading(false)
  }

  const handleChatSend = async (message) => {
    if (!memory) return
    setChatLoading(true)

    setChatMessages(prev => [...prev, {
      id: `temp-${Date.now()}`,
      role: 'reviewer',
      content: message,
      created_at: new Date().toISOString(),
    }])

    try {
      const res = await sendChatMessage(memory.id, currentUser.id, message)
      setChatMessages(prev => [...prev.filter(m => !m.id.startsWith('temp-')), {
        id: `rev-${Date.now()}`,
        role: 'reviewer',
        content: message,
        created_at: new Date().toISOString(),
      }, res.data.ai_message])

      if (res.data.reasoning_update) {
        const memRes = await getMemory(memory.id)
        setMemory(memRes.data)
      }
    } catch (e) {
      console.error('Chat error:', e)
    }
    setChatLoading(false)
  }

  const handleApprove = async () => {
    if (!memory) return
    try {
      const res = await approveMemory(memory.id, currentUser.id)
      setMemory(res.data)
      setStep(4)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Approval failed.')
    }
  }

  const handleReject = async (reason) => {
    if (!memory) return
    try {
      const res = await rejectMemory(memory.id, currentUser.id, reason)
      setMemory(res.data)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Rejection failed.')
    }
  }

  const handleEdit = () => setIsEditing(true)

  const handleSaveEdit = async (updatedReasoning) => {
    if (!memory) return
    try {
      const res = await editMemoryReasoning(memory.id, currentUser.id, updatedReasoning)
      setMemory(res.data)
      setIsEditing(false)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Edit failed.')
    }
  }

  const handleDiscard = async () => {
    if (!memory) return
    if (!confirm('Are you sure you want to discard this memory?')) return
    try {
      await api.patch(`/memory/${memory.id}/discard`, { user_id: currentUser.id })
      navigate('/dashboard')
    } catch (e) {
      alert(e.response?.data?.detail || 'Discard failed.')
    }
  }

  const handleSubmitForReview = async (reviewerId) => {
    if (!memory) return
    try {
      const res = await api.patch(`/memory/${memory.id}/submit-for-review`, {
        user_id: currentUser.id,
        reviewer_id: reviewerId,
      })
      setMemory(res.data)
      setStep(4)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Submit failed.')
    }
  }

  const handleRollback = async (reason) => {
    if (!memory) return
    try {
      const res = await rollbackMemory(memory.id, currentUser.id, reason)
      setMemory(res.data)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Rollback failed.')
    }
  }

  const handleUpdateExisting = async (existingMemory) => {
    if (!existingMemory || !memory) return
    setIsLoading(true)
    try {
      const res = await api.post(`/memory/${existingMemory.id}/merge`, {
        source_memory_id: memory.id,
        user_id: currentUser.id,
      })
      setMemory(res.data)
      setDuplicateWarning(null)
      await loadAuditLog(existingMemory.id)
      await loadChatHistory(existingMemory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to update existing memory.')
    }
    setIsLoading(false)
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate('/dashboard')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-white/60" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">
            {memoryId ? 'Review Memory' : 'Create Organizational Memory'}
          </h1>
          <p className="text-sm text-white/40">Upload documents → AI analyzes → Human validates → Memory stored</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-2 mb-8 overflow-x-auto">
        {STEPS.map((s, idx) => {
          const Icon = s.icon
          const isActive = step >= s.id
          const isCurrent = step === s.id
          return (
            <div key={s.id} className="flex items-center gap-2">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                isCurrent ? 'bg-primary-600/20 border border-primary-500/30 text-primary-300'
                : isActive ? 'bg-emerald-600/10 border border-emerald-500/20 text-emerald-300'
                : 'bg-white/5 border border-white/10 text-white/30'
              }`}>
                {isActive && step > s.id ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                <span className="text-sm font-medium whitespace-nowrap">{s.label}</span>
              </div>
              {idx < STEPS.length - 1 && (
                <div className={`w-8 h-px ${isActive ? 'bg-primary-500/50' : 'bg-white/10'}`} />
              )}
            </div>
          )
        })}
      </div>

      {/* Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <AnimatePresence mode="wait">
            {step === 1 && !memoryId && (
              <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <FileUpload files={files} setFiles={setFiles} onGenerate={handleGenerate} isLoading={isLoading} />
              </motion.div>
            )}

            {step >= 2 && memory && (
              <motion.div key="analysis" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <ChangeDetection
                  changeType={memory.change_type}
                  confidence={memory.confidence}
                  detectionReasons={memory.detection_reasons || []}
                  riskLevel={memory.risk_level}
                />

                {piiWarnings.length > 0 && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-5 border-red-500/30 bg-red-500/5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-9 h-9 bg-red-500/20 rounded-xl flex items-center justify-center">
                        <span className="text-red-400 text-lg">🛡️</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-red-300">PII Detected & Redacted</h4>
                        <p className="text-xs text-white/40">Sensitive information was automatically removed</p>
                      </div>
                    </div>
                    {piiWarnings.map((warn, idx) => (
                      <div key={idx} className="p-3 bg-red-500/5 rounded-lg border border-red-500/10 mb-2 last:mb-0">
                        <p className="text-sm text-white/80 font-medium">{warn.filename}</p>
                        <ul className="mt-1 space-y-1">
                          {warn.issues.map((issue, i) => (
                            <li key={i} className="text-xs text-red-300/70 flex items-center gap-2">
                              <span>🚫</span> {issue}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </motion.div>
                )}

                {duplicateWarning && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-5 border-amber-500/30 bg-amber-500/5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-9 h-9 bg-amber-500/20 rounded-xl flex items-center justify-center">
                        <span className="text-amber-400 text-lg">⚠️</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-amber-300">Similar Memory Already Exists</h4>
                        <p className="text-xs text-white/40">{duplicateWarning.message}</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      {duplicateWarning.memories.map((mem, idx) => (
                        <div key={idx} className="p-3 bg-amber-500/5 rounded-lg border border-amber-500/10 flex items-center justify-between">
                          <div>
                            <p className="text-sm text-white/80 font-medium">{mem.change_type}</p>
                            <p className="text-xs text-white/40">Status: {mem.status} · Confidence: {mem.confidence}%</p>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            mem.status === 'VERIFIED' ? 'bg-emerald-500/20 text-emerald-300' :
                            mem.status === 'DRAFT' ? 'bg-blue-500/20 text-blue-300' :
                            'bg-gray-500/20 text-gray-300'
                          }`}>{mem.status}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center gap-3 mt-4">
                      <button
                        onClick={() => handleUpdateExisting(duplicateWarning.memories.find(m => m.status === 'VERIFIED') || duplicateWarning.memories[0])}
                        className="btn-primary text-sm px-4 py-2"
                      >
                        Update Existing Memory
                      </button>
                      <span className="text-xs text-white/30">or continue below to create a new one</span>
                    </div>
                  </motion.div>
                )}

                <GuardrailAlert flags={memory.guardrail_flags} />

                {isEditing ? (
                  <EditableReasoningRecord
                    reasoning={memory.reasoning}
                    onSave={handleSaveEdit}
                    onCancel={() => setIsEditing(false)}
                  />
                ) : (
                  <ReasoningRecord reasoning={memory.reasoning} />
                )}

                <MissingInfo items={memory.missing_info} />

                <ApprovalBar
                  memory={memory}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEdit={handleEdit}
                  onDiscard={handleDiscard}
                  onSubmitForReview={handleSubmitForReview}
                  onRollback={handleRollback}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {step === 4 && memory?.status === 'VERIFIED' && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-8 text-center border-emerald-500/20">
              <div className="w-16 h-16 mx-auto mb-4 bg-emerald-500/20 rounded-2xl flex items-center justify-center">
                <Check className="w-8 h-8 text-emerald-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Memory Verified</h3>
              <p className="text-white/50 text-sm">This reasoning record is now part of verified organizational memory.</p>
            </motion.div>
          )}

          {step === 4 && memory?.status === 'PENDING_REVIEW' && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-8 text-center border-amber-500/20">
              <div className="w-16 h-16 mx-auto mb-4 bg-amber-500/20 rounded-2xl flex items-center justify-center">
                <Send className="w-8 h-8 text-amber-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Sent for Review</h3>
              <p className="text-white/50 text-sm">Your memory has been submitted for approval. You'll be notified when reviewed.</p>
              <button onClick={() => navigate('/dashboard')} className="btn-secondary mt-4">
                Back to Dashboard
              </button>
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {step >= 3 && memory && (
            <ChatPanel messages={chatMessages} onSend={handleChatSend} isLoading={chatLoading} />
          )}
          <AuditTimeline entries={auditLog} />
        </div>
      </div>
    </div>
  )
}
