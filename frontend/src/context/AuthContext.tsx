'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_BASE_URL } from '@/lib/api-config'

interface Doctor {
  id: number
  name: string
  email: string
  specialization: string
  clinic_name: string
}

interface AuthContextType {
  doctor: Doctor | null
  token: string | null
  isLoggedIn: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  doctor: null,
  token: null,
  isLoggedIn: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [doctor, setDoctor] = useState<Doctor | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const savedToken = localStorage.getItem('medai_token')
    const savedDoctor = localStorage.getItem('medai_doctor')
    if (savedToken && savedDoctor) {
      setToken(savedToken)
      setDoctor(JSON.parse(savedDoctor))
    }
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
    setToken(data.token)
    setDoctor(data.doctor)
    localStorage.setItem('medai_token', data.token)
    localStorage.setItem('medai_doctor', JSON.stringify(data.doctor))
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
    const doctorData = { id: 0, name: formData.name, email: formData.email, specialization: formData.specialization, clinic_name: formData.clinic_name }
    setToken(data.token)
    setDoctor(doctorData)
    localStorage.setItem('medai_token', data.token)
    localStorage.setItem('medai_doctor', JSON.stringify(doctorData))
  }

  const logout = () => {
    setToken(null)
    setDoctor(null)
    localStorage.removeItem('medai_token')
    localStorage.removeItem('medai_doctor')
  }

  return (
    <AuthContext.Provider value={{ doctor, token, isLoggedIn: !!token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
