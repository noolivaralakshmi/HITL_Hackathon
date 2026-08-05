import { createContext, useContext, useState } from 'react'

const UserContext = createContext(null)

export function UserProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null)

  const login = (user) => {
    setCurrentUser(user)
    localStorage.setItem('hitl_user', JSON.stringify(user))
  }

  const logout = () => {
    setCurrentUser(null)
    localStorage.removeItem('hitl_user')
  }

  // Restore from localStorage on mount
  if (!currentUser) {
    const stored = localStorage.getItem('hitl_user')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        if (parsed && parsed.id) {
          setCurrentUser(parsed)
        }
      } catch {}
    }
  }

  const isReviewer = currentUser?.role === 'contributor+reviewer'

  return (
    <UserContext.Provider value={{ currentUser, login, logout, isReviewer }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within UserProvider')
  return context
}
