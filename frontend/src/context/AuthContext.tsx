'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'

interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
  login: (token: string, refreshToken?: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [initialized, setInitialized] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  // Protected routes that require authentication
  const protectedRoutes = ['/analyzer', '/dashboard', '/history']
  // Public routes that authenticated users should be redirected from
  const authRoutes = ['/login', '/signup']

  // Initialize: Check for token in localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
    }
    setInitialized(true)
    setIsLoading(false)
  }, [])

  // Handle route protection only after initialization
  useEffect(() => {
    if (!initialized || isLoading) return

    const isProtectedRoute = protectedRoutes.some(route => pathname?.startsWith(route))
    const isAuthRoute = authRoutes.some(route => pathname?.startsWith(route))

    if (isProtectedRoute && !token) {
      router.push('/login')
    } else if (isAuthRoute && token) {
      router.push('/analyzer')
    }
  }, [token, pathname, isLoading, initialized, router])

  const login = (newToken: string, refreshToken?: string) => {
    localStorage.setItem('token', newToken)
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }
    setToken(newToken)
    router.push('/analyzer')
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    setToken(null)
    router.push('/')
  }

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated: !!token, 
      isLoading: isLoading || !initialized, 
      token, 
      login, 
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
