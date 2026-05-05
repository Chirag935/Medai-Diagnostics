'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_BASE_URL } from '@/lib/api-config'

type UserRole = 'patient' | 'doctor' | 'receptionist'

interface User {
  id: number
  name: string
  email: string
  role: UserRole
  specialization: string
  clinic_name: string
}

// Module access matrix
const MODULE_ACCESS: Record<string, UserRole[]> = {
  'symptom-checker': ['patient', 'doctor'],
  'skin-analyzer': ['patient', 'doctor'],
  'ai-assistant': ['patient', 'doctor'],
  'patients': ['doctor', 'receptionist'],
  'appointments': ['receptionist', 'doctor', 'patient'],
  'prescription': ['doctor'],
  'mlops-dashboard': ['doctor'],
}

interface AuthContextType {
  user: User | null
  doctor: User | null  // backward compat
  token: string | null
  isLoggedIn: boolean
  role: UserRole | null
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  hasAccess: (module: string) => boolean
  isLoaded: boolean
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  doctor: null,
  token: null,
  isLoggedIn: false,
  role: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  hasAccess: () => false,
  isLoaded: false,
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    const savedToken = localStorage.getItem('medai_token')
    const savedUser = localStorage.getItem('medai_user')
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
    }
    setIsLoaded(true)
  }, [])

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API_BASE_URL}/api/patients/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Login failed')
    }
    const data = await res.json()
    const userData: User = data.user || {
      id: data.doctor?.id || 0,
      name: data.doctor?.name || '',
      email: data.doctor?.email || email,
      role: 'doctor' as UserRole,
      specialization: data.doctor?.specialization || '',
      clinic_name: data.doctor?.clinic_name || '',
    }
    setToken(data.token)
    setUser(userData)
    localStorage.setItem('medai_token', data.token)
    localStorage.setItem('medai_user', JSON.stringify(userData))
    // Keep backward compat
    localStorage.setItem('medai_doctor', JSON.stringify(userData))
  }

  const register = async (formData: any) => {
    const res = await fetch(`${API_BASE_URL}/api/patients/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Registration failed')
    }
    const data = await res.json()
    const userData: User = data.user || {
      id: 0,
      name: formData.name,
      email: formData.email,
      role: formData.role || 'patient',
      specialization: formData.specialization || '',
      clinic_name: formData.clinic_name || '',
    }
    setToken(data.token)
    setUser(userData)
    localStorage.setItem('medai_token', data.token)
    localStorage.setItem('medai_user', JSON.stringify(userData))
    localStorage.setItem('medai_doctor', JSON.stringify(userData))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('medai_token')
    localStorage.removeItem('medai_user')
    localStorage.removeItem('medai_doctor')
  }

  const hasAccess = (module: string): boolean => {
    if (!user) return false
    const allowed = MODULE_ACCESS[module]
    if (!allowed) return true  // unknown modules are accessible
    return allowed.includes(user.role)
  }

  return (
    <AuthContext.Provider value={{
      user,
      doctor: user,  // backward compat
      token,
      isLoggedIn: !!token,
      isLoaded,
      role: user?.role || null,
      login,
      register,
      logout,
      hasAccess,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
