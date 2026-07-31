import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Documents
export const uploadDocuments = (files) => {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  return api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getDocumentsByMemory = (memoryId) =>
  api.get(`/documents/memory/${memoryId}`)

// Memory
export const generateMemory = (documentIds, userId) =>
  api.post('/memory/generate', { document_ids: documentIds, user_id: userId })

export const getMemory = (memoryId) =>
  api.get(`/memory/${memoryId}`)

export const listMemories = (status = null) =>
  api.get('/memory', { params: status ? { status } : {} })

export const approveMemory = (memoryId, userId) =>
  api.patch(`/memory/${memoryId}/approve`, { user_id: userId })

export const rejectMemory = (memoryId, userId, reason) =>
  api.patch(`/memory/${memoryId}/reject`, { user_id: userId, reason })

export const editMemoryReasoning = (memoryId, userId, reasoning) =>
  api.patch(`/memory/${memoryId}/edit`, { user_id: userId, reasoning })

export const rollbackMemory = (memoryId, userId, reason) =>
  api.post(`/memory/${memoryId}/rollback`, { user_id: userId, reason })

export const addDocumentsToMemory = (memoryId, documentIds, userId) =>
  api.post(`/memory/${memoryId}/add-documents`, { document_ids: documentIds, user_id: userId })

export const getSnapshots = (memoryId) =>
  api.get(`/memory/${memoryId}/snapshots`)

// Chat
export const sendChatMessage = (memoryId, userId, message) =>
  api.post(`/chat/${memoryId}`, { user_id: userId, message })

export const getChatHistory = (memoryId) =>
  api.get(`/chat/${memoryId}`)

// Query (Mode 2)
export const queryKnowledge = (question) =>
  api.post('/query', { question })

// Users
export const getUsers = () => api.get('/users')

// Audit
export const getAuditLog = (memoryId) => api.get(`/audit/${memoryId}`)

// Demo
export const loadDemo = () => api.get('/demo/load')

export default api
