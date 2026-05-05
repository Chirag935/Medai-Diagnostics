'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, CalendarClock, Plus, Search, User, Stethoscope, Clock, CheckCircle2, XCircle, RefreshCw } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { API, API_BASE_URL } from '@/lib/api-config'

interface Appointment {
  id: number
  patient_id: number
  doctor_id: number
  patient_name: string
  doctor_name: string
  doctor_specialization: string
  symptoms: string
  diagnosis_from_checker: string
  status: string
  appointment_date: string
  appointment_time: string
  notes: string
  created_at: string
}

interface UserOption {
  id: number
  name: string
  email?: string
  phone?: string
  specialization?: string
  clinic_name?: string
}

export default function AppointmentsPage() {
  const router = useRouter()
  const { user, token, role, isLoggedIn } = useAuth()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [patients, setPatients] = useState<UserOption[]>([])
  const [doctors, setDoctors] = useState<UserOption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const [form, setForm] = useState({
    patient_id: 0,
    doctor_id: 0,
    symptoms: '',
    diagnosis_from_checker: '',
    appointment_date: '',
    appointment_time: '',
    notes: '',
  })

  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login')
      return
    }
    fetchAppointments()
    if (role === 'receptionist') {
      fetchPatients()
      fetchDoctors()
    }
  }, [isLoggedIn, role])

  const fetchAppointments = async () => {
    setIsLoading(true)
    try {
      const res = await fetch(`${API.appointments}/list?token=${token}`)
      if (res.ok) {
        const data = await res.json()
        setAppointments(data)
      }
    } catch (e) {
      console.error('Failed to fetch appointments:', e)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchPatients = async () => {
    try {
      const res = await fetch(`${API.appointments}/patients-list?token=${token}`)
      if (res.ok) setPatients(await res.json())
    } catch (e) { console.error(e) }
  }

  const fetchDoctors = async () => {
    try {
      const res = await fetch(`${API.appointments}/doctors-list?token=${token}`)
      if (res.ok) setDoctors(await res.json())
    } catch (e) { console.error(e) }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.patient_id || !form.doctor_id || !form.appointment_date || !form.appointment_time) return
    setIsSubmitting(true)
    try {
      const res = await fetch(`${API.appointments}/create?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (res.ok) {
        setShowForm(false)
        setForm({ patient_id: 0, doctor_id: 0, symptoms: '', diagnosis_from_checker: '', appointment_date: '', appointment_time: '', notes: '' })
        await fetchAppointments()
      }
    } catch (e) { console.error(e) }
    finally { setIsSubmitting(false) }
  }

  const updateStatus = async (id: number, status: string) => {
    try {
      await fetch(`${API.appointments}/update/${id}?token=${token}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      await fetchAppointments()
    } catch (e) { console.error(e) }
  }

  const filteredAppointments = appointments.filter(a => {
    const matchesSearch = a.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.doctor_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.symptoms?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const statusColors: Record<string, string> = {
    scheduled: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    cancelled: 'bg-red-500/10 text-red-400 border-red-500/20',
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-4">
            <button onClick={() => router.push('/')} className="flex items-center text-teal-400 hover:text-teal-300 transition-colors">
              <ArrowLeft className="w-5 h-5 mr-2" /> Back
            </button>
            <div>
              <h1 className="text-4xl font-bold text-white flex items-center gap-3">
                <CalendarClock className="w-9 h-9 text-sky-400" />
                Appointments
              </h1>
              <p className="text-slate-400 mt-1">
                {role === 'receptionist' ? 'Schedule and manage patient appointments' :
                 role === 'doctor' ? 'View your scheduled appointments' :
                 'View your appointment status'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={fetchAppointments} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-sm border border-slate-700 transition-colors">
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
            {role === 'receptionist' && (
              <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white rounded-xl text-sm font-semibold transition-colors">
                <Plus className="w-4 h-4" /> New Appointment
              </button>
            )}
          </div>
        </div>

        {/* Create Form */}
        {showForm && role === 'receptionist' && (
          <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-6 mb-8">
            <h3 className="text-lg font-bold text-white mb-4">Schedule New Appointment</h3>
            <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Patient *</label>
                <select
                  required
                  value={form.patient_id}
                  onChange={e => setForm({...form, patient_id: Number(e.target.value)})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm focus:border-sky-500 focus:outline-none"
                >
                  <option value={0}>Select patient...</option>
                  {patients.map(p => (
                    <option key={p.id} value={p.id}>{p.name} {p.phone ? `(${p.phone})` : ''}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Doctor *</label>
                <select
                  required
                  value={form.doctor_id}
                  onChange={e => setForm({...form, doctor_id: Number(e.target.value)})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm focus:border-sky-500 focus:outline-none"
                >
                  <option value={0}>Select doctor...</option>
                  {doctors.map(d => (
                    <option key={d.id} value={d.id}>Dr. {d.name} — {d.specialization}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Date *</label>
                <input
                  type="date"
                  required
                  value={form.appointment_date}
                  onChange={e => setForm({...form, appointment_date: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Time *</label>
                <input
                  type="time"
                  required
                  value={form.appointment_time}
                  onChange={e => setForm({...form, appointment_time: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Symptoms / Reason</label>
                <input
                  type="text"
                  value={form.symptoms}
                  onChange={e => setForm({...form, symptoms: e.target.value})}
                  placeholder="e.g. Fever, headache"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm placeholder:text-slate-600 focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Notes</label>
                <input
                  type="text"
                  value={form.notes}
                  onChange={e => setForm({...form, notes: e.target.value})}
                  placeholder="Additional notes..."
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 px-3 text-white text-sm placeholder:text-slate-600 focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div className="md:col-span-2 lg:col-span-3 flex gap-3 justify-end">
                <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm hover:bg-slate-700 transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={isSubmitting} className="px-6 py-2 bg-sky-500 text-white rounded-xl text-sm font-semibold hover:bg-sky-600 transition-colors disabled:opacity-50">
                  {isSubmitting ? 'Scheduling...' : 'Schedule Appointment'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              placeholder="Search patients, doctors..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-600 focus:border-sky-500 focus:outline-none"
            />
          </div>
          <div className="flex gap-2">
            {['all', 'scheduled', 'completed', 'cancelled'].map(s => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${
                  statusFilter === s ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
          <div className="text-sm text-slate-500">
            {filteredAppointments.length} appointment{filteredAppointments.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Appointments Table */}
        {isLoading ? (
          <div className="flex items-center justify-center py-32">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-500" />
          </div>
        ) : filteredAppointments.length === 0 ? (
          <div className="text-center py-20 text-slate-500">
            <CalendarClock className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-lg font-semibold">No appointments found</p>
            <p className="text-sm mt-1">
              {role === 'receptionist' ? 'Click "New Appointment" to schedule one.' : 'No appointments scheduled for you yet.'}
            </p>
          </div>
        ) : (
          <div className="bg-slate-900/50 border border-white/5 rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">ID</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">Patient</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">Doctor</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">Date & Time</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">Symptoms</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold">Status</th>
                    {(role === 'receptionist' || role === 'doctor') && (
                      <th className="text-left py-3 px-4 text-slate-400 font-semibold">Actions</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {filteredAppointments.map(appt => (
                    <tr key={appt.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-4 text-slate-500 font-mono">#{appt.id}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-blue-400" />
                          <span className="text-white font-medium">{appt.patient_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Stethoscope className="w-4 h-4 text-teal-400" />
                          <div>
                            <div className="text-white font-medium">Dr. {appt.doctor_name}</div>
                            <div className="text-xs text-slate-500">{appt.doctor_specialization}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-slate-500" />
                          <div>
                            <div className="text-white">{appt.appointment_date}</div>
                            <div className="text-xs text-slate-500">{appt.appointment_time}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-300 max-w-[200px] truncate">{appt.symptoms || '—'}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${statusColors[appt.status] || 'bg-slate-800 text-slate-400'}`}>
                          {appt.status}
                        </span>
                      </td>
                      {(role === 'receptionist' || role === 'doctor') && (
                        <td className="py-3 px-4">
                          {appt.status === 'scheduled' && (
                            <div className="flex gap-1">
                              <button
                                onClick={() => updateStatus(appt.id, 'completed')}
                                className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors"
                                title="Mark completed"
                              >
                                <CheckCircle2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => updateStatus(appt.id, 'cancelled')}
                                className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                                title="Cancel"
                              >
                                <XCircle className="w-4 h-4" />
                              </button>
                            </div>
                          )}
                          {appt.status !== 'scheduled' && (
                            <span className="text-xs text-slate-600">—</span>
                          )}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
