'use client'

import { useState } from 'react'
import { ArrowLeft, LogIn, UserPlus, Stethoscope, Mail, Lock, Building2, GraduationCap } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { useLanguage } from '@/context/LanguageContext'

export default function LoginPage() {
  const router = useRouter()
  const { login, register } = useAuth()
  const { t } = useLanguage()
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    specialization: 'General Medicine',
    clinic_name: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (isRegister) {
        await register(form)
      } else {
        await login(form.email, form.password)
      }
      router.push('/patients')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Back button */}
        <button onClick={() => router.push('/')} className="flex items-center text-teal-400 hover:text-teal-300 mb-8 transition-colors">
          <ArrowLeft className="w-5 h-5 mr-2" />
          {t('common.back')}
        </button>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-teal-500 to-cyan-500 rounded-2xl flex items-center justify-center mb-4 shadow-2xl shadow-teal-500/20">
            <Stethoscope className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">MedAI Diagnostics</h1>
          <p className="text-slate-400 text-sm mt-1">Professional Clinical Portal</p>
        </div>

        {/* Card */}
        <div className="bg-[#0a1225] border border-white/[0.06] rounded-2xl p-8">
          {/* Toggle */}
          <div className="flex bg-slate-900 rounded-xl p-1 mb-6">
            <button
              onClick={() => setIsRegister(false)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${
                !isRegister ? 'bg-teal-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'
              }`}
            >
              <LogIn className="w-4 h-4" />
              {t('auth.login')}
            </button>
            <button
              onClick={() => setIsRegister(true)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isRegister ? 'bg-teal-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'
              }`}
            >
              <UserPlus className="w-4 h-4" />
              {t('auth.register')}
            </button>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-xl mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">{t('auth.doctorName')}</label>
                  <div className="relative">
                    <Stethoscope className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      type="text"
                      required
                      value={form.name}
                      onChange={e => setForm({...form, name: e.target.value})}
                      placeholder="Dr. John Smith"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-teal-500 transition-colors text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">{t('auth.clinicName')}</label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      type="text"
                      value={form.clinic_name}
                      onChange={e => setForm({...form, clinic_name: e.target.value})}
                      placeholder="City Hospital"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-teal-500 transition-colors text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1.5 block">{t('auth.specialization')}</label>
                  <div className="relative">
                    <GraduationCap className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <select
                      value={form.specialization}
                      onChange={e => setForm({...form, specialization: e.target.value})}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-teal-500 transition-colors text-sm appearance-none"
                    >
                      {['General Medicine', 'Dermatology', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'ENT', 'Ophthalmology', 'Psychiatry', 'Other'].map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="text-xs text-slate-400 mb-1.5 block">{t('auth.email')}</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={e => setForm({...form, email: e.target.value})}
                  placeholder="doctor@clinic.com"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-teal-500 transition-colors text-sm"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1.5 block">{t('auth.password')}</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  required
                  value={form.password}
                  onChange={e => setForm({...form, password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-teal-500 transition-colors text-sm"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:shadow-teal-500/20 transition-all disabled:opacity-50 mt-2"
            >
              {isLoading ? t('common.loading') : (isRegister ? t('auth.register') : t('auth.login'))}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
