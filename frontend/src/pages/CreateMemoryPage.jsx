import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Check, Upload as UploadIcon, Sparkles, MessageSquare, FileCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import {
  uploadDocuments, generateMemory, getMemory, listMemories,
  approveMemory, rejectMemory, editMemoryReasoning, rollbackMemory,
  sendChatMessage, getChatHistory, getAuditLog
} from '../api/client'

import FileUpload from '../components/FileUpload'
import ChangeDetection from '../components/ChangeDetection'
import ReasoningRecord from '../components/ReasoningRecord'
import MissingInfo from '../components/MissingInfo'
import ChatPanel from '../components/ChatPanel'
import ApprovalBar from '../components/ApprovalBar'
import AuditTimeline from '../components/AuditTimeline'
import GuardrailAlert from '../components/GuardrailAlert'

const STEPS = [
  { id: 1, label: 'Upload', icon: UploadIcon },
  { id: 2, label: 'Analysis', icon: Sparkles },
  { id: 3, label: 'Review', icon: MessageSquare },
  { id: 4, label: 'Approve', icon: FileCheck },
]

export default function CreateMemoryPage() {
  const navigate = useNavigate()
  const { currentUser } = useUser()
  const [step, setStep] = useState(1)
  const [files, setFiles] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [memory, setMemory] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)
  const [auditLog, setAuditLog] = useState([])
  const [existingMemories, setExistingMemories] = useState([])

  // Load existing memories on mount
  useEffect(() => {
    listMemories().then(res => {
      setExistingMemories(res.data?.memories || [])
    }).catch(() => {})
  }, [])

  // Only auto-load if there's a DRAFT memory in progress
  useEffect(() => {
    if (existingMemories.length > 0 && !memory) {
      const draft = existingMemories.find(m => m.status === 'DRAFT')
      if (draft) {
        setMemory(draft)
        setStep(3)
        loadAuditLog(draft.id)
        loadChatHistory(draft.id)
      }
    }
  }, [existingMemories])

  const loadAuditLog = async (memoryId) => {
    try {
      const res = await getAuditLog(memoryId)
      setAuditLog(res.data?.log || [])
    } catch (e) {}
  }

  const loadChatHistory = async (memoryId) => {
    try {
      const res = await getChatHistory(memoryId)
      setChatMessages(res.data?.messages || [])
    } catch (e) {}
  }

  const handleGenerate = async () => {
    if (files.length === 0) return
    setIsLoading(true)

    try {
      // Upload documents
      const uploadRes = await uploadDocuments(files)
      const docIds = uploadRes.data.documents.map(d => d.id)

      // Generate memory
      const genRes = await generateMemory(docIds, currentUser.id)
      setMemory(genRes.data)
      setStep(2)

      // Load audit log
      await loadAuditLog(genRes.data.id)

      // Auto advance to step 3
      setTimeout(() => setStep(3), 1500)
    } catch (e) {
      console.error('Error generating memory:', e)
    }
    setIsLoading(false)
  }

  const handleChatSend = async (message) => {
    if (!memory) return
    setChatLoading(true)

    // Optimistic add
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

      // If reasoning updated, refresh memory
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
      alert(e.response?.data?.detail || 'Approval failed. Check your role permissions.')
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

  const handleEdit = async () => {
    // For demo: just show a message. In production you'd open an editor.
    alert('Edit mode: In production, this would open an inline editor for the reasoning record.')
  }

  const handleRollback = async (reason) => {
    if (!memory) return
    try {
      const res = await rollbackMemory(memory.id, currentUser.id, reason)
      setMemory(res.data)
      await loadAuditLog(memory.id)
    } catch (e) {
      alert(e.response?.data?.detail || 'Rollback failed. Admin role required.')
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-white/60" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Create Organizational Memory</h1>
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
              <div
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                  isCurrent
                    ? 'bg-primary-600/20 border border-primary-500/30 text-primary-300'
                    : isActive
                    ? 'bg-emerald-600/10 border border-emerald-500/20 text-emerald-300'
                    : 'bg-white/5 border border-white/10 text-white/30'
                }`}
              >
                {isActive && step > s.id ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
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
        {/* Main Content - 2 cols */}
        <div className="lg:col-span-2 space-y-6">
          <AnimatePresence mode="wait">
            {step === 1 && (
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

                <GuardrailAlert flags={memory.guardrail_flags} />

                <ReasoningRecord reasoning={memory.reasoning} />

                <MissingInfo items={memory.missing_info} />

                <ApprovalBar
                  memory={memory}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEdit={handleEdit}
                  onRollback={handleRollback}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {step === 4 && memory?.status === 'VERIFIED' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-8 text-center border-emerald-500/20"
            >
              <div className="w-16 h-16 mx-auto mb-4 bg-emerald-500/20 rounded-2xl flex items-center justify-center">
                <Check className="w-8 h-8 text-emerald-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Memory Verified</h3>
              <p className="text-white/50 text-sm">
                This reasoning record is now part of your organizational memory.
                It will be used to answer future questions in the Knowledge Assistant.
              </p>
            </motion.div>
          )}
        </div>

        {/* Sidebar - 1 col */}
        <div className="space-y-6">
          {step >= 3 && memory && (
            <ChatPanel
              messages={chatMessages}
              onSend={handleChatSend}
              isLoading={chatLoading}
            />
          )}

          <AuditTimeline entries={auditLog} />
        </div>
      </div>
    </div>
  )
}
