import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, Bot, User, Search, FileText, CheckCircle, XCircle, ArrowRight, ExternalLink } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { queryKnowledge } from '../api/client'
import api from '../api/client'

function EvidenceChip({ filename, memoryId }) {
  const [url, setUrl] = useState(null)

  useEffect(() => {
    if (memoryId) {
      api.get(`/documents/memory/${memoryId}`)
        .then(res => {
          const docs = res.data?.documents || []
          const match = docs.find(d =>
            d.filename === filename ||
            d.filename.toLowerCase().includes(filename.toLowerCase().replace('.pdf', '').replace('.txt', ''))
          )
          if (match?.download_url) setUrl(match.download_url)
        })
        .catch(() => {})
    }
  }, [filename, memoryId])

  if (url) {
    return (
      <a href={url} target="_blank" rel="noopener noreferrer"
        className="inline-flex items-center gap-1 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300 hover:bg-blue-500/20 hover:text-blue-200 transition-all cursor-pointer">
        <FileText className="w-3 h-3" />
        {filename}
        <ExternalLink className="w-2.5 h-2.5" />
      </a>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300">
      <FileText className="w-3 h-3" />
      {filename}
    </span>
  )
}

export default function QueryPage() {
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [conversations, setConversations] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim() || isLoading) return

    const q = question.trim()
    setQuestion('')
    setIsLoading(true)

    // Add question to conversation
    setConversations(prev => [...prev, { type: 'question', content: q }])

    try {
      const res = await queryKnowledge(q)
      setConversations(prev => [...prev, { type: 'answer', data: res.data }])
    } catch (e) {
      setConversations(prev => [...prev, {
        type: 'answer',
        data: {
          found: false,
          message: 'Error connecting to the server. Please ensure the backend is running.',
          possible_reasons: ['Backend server may not be running']
        }
      }])
    }
    setIsLoading(false)
  }

  const renderAnswer = (data) => {
    if (!data.found) {
      return (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 border-amber-500/10"
        >
          <div className="flex items-center gap-3 mb-4">
            <XCircle className="w-5 h-5 text-amber-400" />
            <p className="text-white font-medium">No Verified Memory Found</p>
          </div>
          <p className="text-sm text-white/60 mb-4">{data.message}</p>
          {data.possible_reasons && (
            <div className="space-y-2">
              <p className="text-xs text-white/40 uppercase font-semibold">Possible reasons:</p>
              {data.possible_reasons.map((reason, i) => (
                <p key={i} className="text-sm text-white/50 flex items-center gap-2">
                  <span className="text-amber-400">•</span> {reason}
                </p>
              ))}
            </div>
          )}
          <p className="text-sm text-white/50 mt-4 bg-white/5 border border-white/10 rounded-xl px-4 py-3">
            To create organizational memory, please reach out to the admin team or a contributor to upload relevant documents.
          </p>
        </motion.div>
      )
    }

    const answer = data.answer
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 border-emerald-500/10 space-y-4"
      >
        <div className="flex items-center gap-3 mb-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <p className="text-sm text-emerald-300 font-medium">From Verified Organizational Memory</p>
        </div>

        {/* Summary */}
        <p className="text-white leading-relaxed">{answer.summary}</p>

        {/* Decision */}
        {answer.decision && (
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Decision</p>
            <p className="text-white font-medium">{answer.decision}</p>
          </div>
        )}

        {/* Reason */}
        {answer.reason && (
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Reason</p>
            <p className="text-white/80 text-sm">{answer.reason}</p>
          </div>
        )}

        {/* Rejected Alternatives */}
        {answer.rejected_alternatives && answer.rejected_alternatives.length > 0 && (
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <p className="text-xs text-white/40 uppercase font-semibold mb-2">Rejected Alternatives</p>
            <div className="space-y-2">
              {answer.rejected_alternatives.map((alt, i) => (
                <div key={i} className="flex items-start gap-2">
                  <XCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-sm text-white font-medium">{alt.name}</span>
                    <span className="text-sm text-white/50"> — {alt.reason}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Evidence */}
        {answer.evidence && answer.evidence.length > 0 && (
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <p className="text-xs text-white/40 uppercase font-semibold mb-2">Evidence</p>
            <div className="flex flex-wrap gap-2">
              {answer.evidence.map((doc, i) => (
                <EvidenceChip key={i} filename={doc} memoryId={answer.memory_id} />
              ))}
            </div>
          </div>
        )}

        {/* Approved by */}
        {answer.approved_by && (
          <p className="text-xs text-white/40">
            Verified by: <span className="text-white/60">{answer.approved_by}</span>
          </p>
        )}
      </motion.div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-white/60" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Verified Organizational Knowledge</h1>
          <p className="text-sm text-white/40">Ask questions. Receive answers ONLY from approved memory.</p>
        </div>
      </div>

      {/* Conversation Area */}
      <div className="space-y-6 mb-6 min-h-[400px]">
        {conversations.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-emerald-600/20 rounded-2xl flex items-center justify-center border border-emerald-500/30">
              <Search className="w-8 h-8 text-emerald-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Ask about past decisions</h3>
            <p className="text-sm text-white/40 max-w-md mx-auto">
              Your questions will be answered exclusively from verified organizational memory.
              No hallucination. No general AI knowledge.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-xl mx-auto">
              {[
                'Why did we choose Passkeys instead of MFA Tokens?',
                'What risks were accepted for the authentication migration?',
                'Who approved the passkey implementation?',
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => setQuestion(q)}
                  className="text-xs px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {conversations.map((item, idx) => (
            <div key={idx}>
              {item.type === 'question' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-end"
                >
                  <div className="max-w-[80%] flex items-start gap-3">
                    <div className="bg-primary-600/30 p-4 rounded-2xl rounded-tr-sm">
                      <p className="text-white">{item.content}</p>
                    </div>
                    <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-primary-400" />
                    </div>
                  </div>
                </motion.div>
              )}
              {item.type === 'answer' && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-emerald-600/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="flex-1">
                    {renderAnswer(item.data)}
                  </div>
                </div>
              )}
            </div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
            <div className="w-8 h-8 bg-emerald-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="glass-card p-4">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="sticky bottom-8">
        <div className="glass-card p-3 flex items-center gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about organizational decisions..."
            className="flex-1 bg-transparent border-0 outline-none text-white placeholder-white/30 px-3 py-2"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!question.trim() || isLoading}
            className="p-3 bg-primary-600 hover:bg-primary-500 rounded-xl transition-all disabled:opacity-30"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
