import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageSquare, Bot, User } from 'lucide-react'
import { useUser } from '../context/UserContext'

export default function ChatPanel({ messages, onSend, isLoading }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const { currentUser } = useUser()

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <div className="glass-card flex flex-col h-[500px]">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/10 flex items-center gap-3">
        <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
          <MessageSquare className="w-4 h-4 text-primary-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">Review Assistant</h3>
          <p className="text-xs text-white/40">Ask questions about the analysis</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8 text-white/30 text-sm">
            <Bot className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p>Ask the AI about its reasoning.</p>
            <p className="mt-1">Try: "Why did you conclude the business objective is phishing reduction?"</p>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={msg.id || idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'reviewer' ? 'justify-end' : ''}`}
            >
              {msg.role === 'ai' && (
                <div className="w-7 h-7 bg-primary-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Bot className="w-3.5 h-3.5 text-primary-400" />
                </div>
              )}
              <div
                className={`max-w-[80%] p-3 rounded-xl text-sm leading-relaxed ${
                  msg.role === 'reviewer'
                    ? 'bg-primary-600/30 text-white rounded-tr-sm'
                    : 'bg-white/5 text-white/90 border border-white/10 rounded-tl-sm'
                }`}
              >
                {msg.content}
              </div>
              {msg.role === 'reviewer' && (
                <div className="w-7 h-7 bg-emerald-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <User className="w-3.5 h-3.5 text-emerald-400" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
            <div className="w-7 h-7 bg-primary-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-primary-400" />
            </div>
            <div className="bg-white/5 border border-white/10 p-3 rounded-xl rounded-tl-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the reasoning..."
            className="input-field flex-1 py-2.5 text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2.5 bg-primary-600 hover:bg-primary-500 rounded-xl transition-all disabled:opacity-30"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
