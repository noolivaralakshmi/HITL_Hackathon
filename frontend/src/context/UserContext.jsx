import { createContext, useContext, useState, useEffect } from 'react'
import { getUsers } from '../api/client'

const UserContext = createContext(null)

const DEFAULT_USERS = [
  { id: 'user-admin-001', name: 'Sarah Chen', email: 'sarah.chen@company.com', role: 'admin' },
  { id: 'user-approver-001', name: 'Marcus Johnson', email: 'marcus.j@company.com', role: 'approver' },
  { id: 'user-reviewer-001', name: 'Alex Rivera', email: 'alex.r@company.com', role: 'reviewer' },
  { id: 'user-viewer-001', name: 'Jordan Lee', email: 'jordan.l@company.com', role: 'viewer' },
]

export function UserProvider({ children }) {
  const [users, setUsers] = useState(DEFAULT_USERS)
  const [currentUser, setCurrentUser] = useState(DEFAULT_USERS[2]) // Default: reviewer

  useEffect(() => {
    getUsers()
      .then((res) => {
        if (res.data?.users?.length) setUsers(res.data.users)
      })
      .catch(() => {}) // Use defaults on error
  }, [])

  const switchUser = (userId) => {
    const user = users.find((u) => u.id === userId)
    if (user) setCurrentUser(user)
  }

  return (
    <UserContext.Provider value={{ users, currentUser, switchUser }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within UserProvider')
  return context
}
