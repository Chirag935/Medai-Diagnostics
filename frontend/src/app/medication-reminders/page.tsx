'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import {
  Pill, Plus, Trash2, Bell, BellOff, Clock, Calendar,
  CheckCircle2, AlertCircle, ArrowLeft, Sparkles, X
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

// ---------- Types ----------
type Frequency = 'once' | 'daily' | 'twice' | 'thrice' | 'custom'

interface Reminder {
  id: string
  medication: string
  dose: string
  frequency: Frequency
  times: string[]            // ["09:00", "21:00"]
  startDate: string          // ISO yyyy-mm-dd
  endDate?: string
  notes?: string
  active: boolean
  createdAt: number
  history: { ts: number; status: 'taken' | 'snoozed' | 'missed' }[]
}

const STORAGE_KEY = 'medai_medication_reminders_v1'

const FREQ_LABELS: Record<Frequency, string> = {
  once: 'Once a day',
  daily: 'Once a day',
  twice: 'Twice a day',
  thrice: 'Three times a day',
  custom: 'Custom times',
}

const FREQ_DEFAULT_TIMES: Record<Frequency, string[]> = {
  once: ['09:00'],
  daily: ['09:00'],
  twice: ['09:00', '21:00'],
  thrice: ['08:00', '14:00', '20:00'],
  custom: ['09:00'],
}

// ---------- Helpers ----------
function loadReminders(): Reminder[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveReminders(items: Reminder[]) {
  if (typeof window === 'undefined') return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

function isReminderDue(rem: Reminder, now: Date): { due: boolean; time: string | null } {
  if (!rem.active) return { due: false, time: null }
  const todayStr = now.toISOString().slice(0, 10)
  if (rem.startDate && todayStr < rem.startDate) return { due: false, time: null }
  if (rem.endDate && todayStr > rem.endDate) return { due: false, time: null }

  const hh = String(now.getHours()).padStart(2, '0')
  const mm = String(now.getMinutes()).padStart(2, '0')
  const nowHM = `${hh}:${mm}`

  for (const t of rem.times) {
    if (t === nowHM) {
      // Avoid duplicate firing within same minute
      const fired = rem.history.some(h => {
        const d = new Date(h.ts)
        return (
          d.toISOString().slice(0, 10) === todayStr &&
          String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0') === nowHM
        )
      })
      if (!fired) return { due: true, time: t }
    }
  }
  return { due: false, time: null }
}

function nextDoseLabel(rem: Reminder): string {
  if (!rem.active) return 'Paused'
  if (!rem.times.length) return '—'
  const now = new Date()
  const nowMins = now.getHours() * 60 + now.getMinutes()
  const upcoming = rem.times
    .map(t => {
      const [h, m] = t.split(':').map(Number)
      return { t, mins: h * 60 + m }
    })
    .sort((a, b) => a.mins - b.mins)
  const next = upcoming.find(u => u.mins > nowMins)
  if (next) return `Today at ${next.t}`
  return `Tomorrow at ${upcoming[0].t}`
}

// ---------- Page ----------
export default function MedicationRemindersPage() {
  const router = useRouter()
  const { isLoaded, isLoggedIn, hasAccess } = useAuth()

  const [reminders, setReminders] = useState<Reminder[]>([])
  const [showForm, setShowForm] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const [activeAlert, setActiveAlert] = useState<{ rem: Reminder; time: string } | null>(null)
  const tickRef = useRef<number | null>(null)

  // Auth gate
  useEffect(() => {
    if (!isLoaded) return
    if (!isLoggedIn) {
      router.push('/login')
      return
    }
    if (!hasAccess('medication-reminders')) {
      router.push('/')
    }
  }, [isLoaded, isLoggedIn, hasAccess, router])

  // Load + permission
  useEffect(() => {
    setReminders(loadReminders())
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setPermission(Notification.permission)
    }
  }, [])

  const persist = useCallback((items: Reminder[]) => {
    setReminders(items)
    saveReminders(items)
  }, [])

  // Tick: check every 30s for due reminders
  useEffect(() => {
    const check = () => {
      const now = new Date()
      setReminders(prev => {
        let changed = false
        const updated = prev.map(r => {
          const { due, time } = isReminderDue(r, now)
          if (due && time) {
            changed = true
            // fire notification
            if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
              try {
                new Notification(`Time to take ${r.medication}`, {
                  body: `${r.dose} — ${time}${r.notes ? `\n${r.notes}` : ''}`,
                  icon: '/favicon.ico',
                  tag: `${r.id}-${time}`,
                })
              } catch {}
            }
            // also pop in-app modal
            setActiveAlert({ rem: r, time })
            return {
              ...r,
              history: [...r.history, { ts: Date.now(), status: 'missed' as const }],
            }
          }
          return r
        })
        if (changed) saveReminders(updated)
        return updated
      })
    }
    check()
    tickRef.current = window.setInterval(check, 30_000) as unknown as number
    return () => {
      if (tickRef.current) clearInterval(tickRef.current)
    }
  }, [])

  const requestPermission = async () => {
    if (typeof window === 'undefined' || !('Notification' in window)) return
    const p = await Notification.requestPermission()
    setPermission(p)
    if (p === 'granted') {
      try {
        new Notification('MedAI Reminders enabled', {
          body: 'You will be alerted when it\'s time to take your medication.',
          icon: '/favicon.ico',
        })
      } catch {}
    }
  }

  const addReminder = (data: Omit<Reminder, 'id' | 'createdAt' | 'history' | 'active'>) => {
    const r: Reminder = {
      ...data,
      id: crypto.randomUUID(),
      createdAt: Date.now(),
      active: true,
      history: [],
    }
    persist([r, ...reminders])
    setShowForm(false)
  }

  const deleteReminder = (id: string) => {
    if (!confirm('Delete this reminder?')) return
    persist(reminders.filter(r => r.id !== id))
  }

  const toggleActive = (id: string) => {
    persist(reminders.map(r => (r.id === id ? { ...r, active: !r.active } : r)))
  }

  const markAsTaken = (id: string) => {
    persist(reminders.map(r => {
      if (r.id !== id) return r
      // Update most recent missed entry to taken; else append a fresh taken record
      const hist = [...r.history]
      for (let i = hist.length - 1; i >= 0; i--) {
        if (hist[i].status === 'missed') {
          hist[i] = { ...hist[i], status: 'taken' }
          return { ...r, history: hist }
        }
      }
      hist.push({ ts: Date.now(), status: 'taken' })
      return { ...r, history: hist }
    }))
    setActiveAlert(null)
  }

  // Adherence stat
  const adherence = (() => {
    const all = reminders.flatMap(r => r.history)
    if (!all.length) return null
    const taken = all.filter(h => h.status === 'taken').length
    return Math.round((taken / all.length) * 100)
  })()

  if (!isLoaded || !isLoggedIn) {
    return (
      <div className="min-h-screen bg-[#050a18] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-teal-500/20 border-t-teal-500 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#050a18] text-white">
      {/* Ambient bg */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-pink-500/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-rose-500/5 rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative border-b border-white/[0.06] bg-[#050a18]/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Back to Dashboard</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl flex items-center justify-center shadow-lg shadow-pink-500/25">
              <Pill className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold">Medication Reminders</div>
              <div className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">Stay on schedule</div>
            </div>
          </div>
        </div>
      </header>

      <main className="relative max-w-6xl mx-auto px-6 py-8">
        {/* Stats row */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
            <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">Active Reminders</div>
            <div className="text-3xl font-bold">{reminders.filter(r => r.active).length}</div>
            <div className="text-xs text-slate-500 mt-1">{reminders.length} total</div>
          </div>
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
            <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">Adherence Rate</div>
            <div className="text-3xl font-bold text-emerald-400">
              {adherence !== null ? `${adherence}%` : '—'}
            </div>
            <div className="text-xs text-slate-500 mt-1">Doses taken on time</div>
          </div>
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
            <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">Notifications</div>
            <div className="flex items-center gap-2 mt-1">
              {permission === 'granted' ? (
                <>
                  <Bell className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">Enabled</span>
                </>
              ) : permission === 'denied' ? (
                <>
                  <BellOff className="w-5 h-5 text-rose-400" />
                  <span className="text-rose-400 font-semibold">Blocked</span>
                </>
              ) : (
                <button
                  onClick={requestPermission}
                  className="text-xs px-3 py-1.5 rounded-lg bg-pink-500 hover:bg-pink-600 transition font-semibold"
                >
                  Enable browser alerts
                </button>
              )}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {permission === 'denied' ? 'Re-enable in browser settings' : 'Get desktop notifications'}
            </div>
          </div>
        </section>

        {/* Add button */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Your Reminders</h2>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 transition font-semibold text-sm shadow-lg shadow-pink-500/25"
          >
            <Plus className="w-4 h-4" />
            Add Reminder
          </button>
        </div>

        {/* Reminders list */}
        {reminders.length === 0 ? (
          <div className="text-center py-20 rounded-2xl border border-dashed border-white/[0.08]">
            <Pill className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <div className="text-slate-400 mb-1 font-semibold">No reminders yet</div>
            <div className="text-sm text-slate-500">
              Add your first medication to get scheduled alerts.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reminders.map(r => (
              <ReminderCard
                key={r.id}
                rem={r}
                onDelete={() => deleteReminder(r.id)}
                onToggle={() => toggleActive(r.id)}
                onTaken={() => markAsTaken(r.id)}
              />
            ))}
          </div>
        )}

        {/* Tip */}
        <div className="mt-8 flex items-start gap-3 p-4 rounded-xl bg-pink-500/5 border border-pink-500/20">
          <Sparkles className="w-5 h-5 text-pink-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-slate-300">
            <span className="font-semibold text-pink-400">Tip:</span> Reminders run in your browser
            using the Web Notifications API. Keep this tab open in the background to receive alerts
            on time. All data is stored locally on your device — nothing is sent to a server.
          </div>
        </div>
      </main>

      {/* Add form modal */}
      {showForm && (
        <ReminderForm onClose={() => setShowForm(false)} onSubmit={addReminder} />
      )}

      {/* In-app alert */}
      {activeAlert && (
        <DueAlert
          rem={activeAlert.rem}
          time={activeAlert.time}
          onTaken={() => markAsTaken(activeAlert.rem.id)}
          onDismiss={() => setActiveAlert(null)}
        />
      )}
    </div>
  )
}

// ---------- Subcomponents ----------
function ReminderCard({
  rem,
  onDelete,
  onToggle,
  onTaken,
}: {
  rem: Reminder
  onDelete: () => void
  onToggle: () => void
  onTaken: () => void
}) {
  const total = rem.history.length
  const taken = rem.history.filter(h => h.status === 'taken').length
  const adh = total ? Math.round((taken / total) * 100) : null

  return (
    <div className={`rounded-2xl border p-5 transition ${
      rem.active
        ? 'border-white/[0.08] bg-white/[0.02] hover:border-pink-500/30'
        : 'border-white/[0.04] bg-white/[0.01] opacity-60'
    }`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-pink-500/20 to-rose-500/20 border border-pink-500/30 rounded-xl flex items-center justify-center">
            <Pill className="w-5 h-5 text-pink-400" />
          </div>
          <div>
            <div className="font-bold text-white">{rem.medication}</div>
            <div className="text-xs text-slate-400">{rem.dose}</div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onToggle}
            title={rem.active ? 'Pause' : 'Resume'}
            className="p-2 rounded-lg hover:bg-white/[0.04] transition"
          >
            {rem.active ? (
              <Bell className="w-4 h-4 text-emerald-400" />
            ) : (
              <BellOff className="w-4 h-4 text-slate-500" />
            )}
          </button>
          <button
            onClick={onDelete}
            title="Delete"
            className="p-2 rounded-lg hover:bg-rose-500/10 transition"
          >
            <Trash2 className="w-4 h-4 text-slate-500 hover:text-rose-400" />
          </button>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2 text-slate-400">
          <Clock className="w-3.5 h-3.5" />
          <span>{FREQ_LABELS[rem.frequency]}</span>
          <span className="text-slate-600">•</span>
          <span className="text-slate-300">{rem.times.join(', ')}</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <Calendar className="w-3.5 h-3.5" />
          <span>From {rem.startDate}</span>
          {rem.endDate && <><span className="text-slate-600">→</span><span>{rem.endDate}</span></>}
        </div>
        {rem.notes && (
          <div className="text-xs text-slate-500 italic pt-1 border-t border-white/[0.04]">
            {rem.notes}
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-white/[0.04] flex items-center justify-between">
        <div className="text-xs">
          <span className="text-slate-500">Next: </span>
          <span className="text-pink-400 font-semibold">{nextDoseLabel(rem)}</span>
        </div>
        {adh !== null && (
          <div className="text-xs">
            <span className="text-slate-500">Adherence: </span>
            <span className={adh >= 80 ? 'text-emerald-400' : adh >= 50 ? 'text-amber-400' : 'text-rose-400'}>
              {adh}% ({taken}/{total})
            </span>
          </div>
        )}
      </div>

      {rem.active && (
        <button
          onClick={onTaken}
          className="mt-3 w-full px-3 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold transition flex items-center justify-center gap-2"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          Mark Last Dose as Taken
        </button>
      )}
    </div>
  )
}

function ReminderForm({
  onClose,
  onSubmit,
}: {
  onClose: () => void
  onSubmit: (r: Omit<Reminder, 'id' | 'createdAt' | 'history' | 'active'>) => void
}) {
  const [medication, setMedication] = useState('')
  const [dose, setDose] = useState('')
  const [frequency, setFrequency] = useState<Frequency>('daily')
  const [times, setTimes] = useState<string[]>(['09:00'])
  const [startDate, setStartDate] = useState(todayISO())
  const [endDate, setEndDate] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')

  const updateFrequency = (f: Frequency) => {
    setFrequency(f)
    setTimes(FREQ_DEFAULT_TIMES[f])
  }

  const updateTime = (idx: number, val: string) => {
    setTimes(prev => prev.map((t, i) => (i === idx ? val : t)))
  }

  const addTimeSlot = () => setTimes(prev => [...prev, '12:00'])
  const removeTimeSlot = (idx: number) => setTimes(prev => prev.filter((_, i) => i !== idx))

  const handleSubmit = () => {
    if (!medication.trim()) {
      setError('Medication name is required')
      return
    }
    if (!dose.trim()) {
      setError('Dose is required (e.g. "500mg" or "1 tablet")')
      return
    }
    if (!times.length) {
      setError('Add at least one reminder time')
      return
    }
    onSubmit({
      medication: medication.trim(),
      dose: dose.trim(),
      frequency,
      times: [...times].sort(),
      startDate,
      endDate: endDate || undefined,
      notes: notes.trim() || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#0a1124] border border-white/[0.08] rounded-2xl w-full max-w-lg my-8 shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-pink-500 to-rose-500 rounded-lg flex items-center justify-center">
              <Plus className="w-4 h-4 text-white" />
            </div>
            <div className="font-bold">New Reminder</div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/[0.04] transition">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-sm text-rose-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <Field label="Medication name">
            <input
              value={medication}
              onChange={e => setMedication(e.target.value)}
              placeholder="e.g. Metformin"
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
            />
          </Field>

          <Field label="Dose">
            <input
              value={dose}
              onChange={e => setDose(e.target.value)}
              placeholder="e.g. 500mg or 1 tablet"
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
            />
          </Field>

          <Field label="Frequency">
            <select
              value={frequency}
              onChange={e => updateFrequency(e.target.value as Frequency)}
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
            >
              <option value="daily">Once a day</option>
              <option value="twice">Twice a day</option>
              <option value="thrice">Three times a day</option>
              <option value="custom">Custom times</option>
            </select>
          </Field>

          <Field label="Reminder times">
            <div className="space-y-2">
              {times.map((t, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <input
                    type="time"
                    value={t}
                    onChange={e => updateTime(idx, e.target.value)}
                    className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
                  />
                  {frequency === 'custom' && times.length > 1 && (
                    <button
                      onClick={() => removeTimeSlot(idx)}
                      className="p-2 rounded-lg hover:bg-rose-500/10 text-slate-500 hover:text-rose-400 transition"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              {frequency === 'custom' && (
                <button
                  onClick={addTimeSlot}
                  className="w-full px-3 py-2 rounded-lg border border-dashed border-white/[0.1] text-xs text-slate-400 hover:text-white hover:border-pink-500/30 transition"
                >
                  + Add another time
                </button>
              )}
            </div>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Start date">
              <input
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
              />
            </Field>
            <Field label="End date (optional)">
              <input
                type="date"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50"
              />
            </Field>
          </div>

          <Field label="Notes (optional)">
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Take with food, avoid alcohol, etc."
              rows={2}
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500/50 resize-none"
            />
          </Field>
        </div>

        <div className="flex items-center justify-end gap-2 p-5 border-t border-white/[0.06]">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/[0.04] transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-sm font-semibold shadow-lg shadow-pink-500/25 transition"
          >
            Save Reminder
          </button>
        </div>
      </div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs uppercase tracking-wider text-slate-500 mb-1.5 font-semibold">
        {label}
      </span>
      {children}
    </label>
  )
}

function DueAlert({
  rem,
  time,
  onTaken,
  onDismiss,
}: {
  rem: Reminder
  time: string
  onTaken: () => void
  onDismiss: () => void
}) {
  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-sm rounded-2xl border border-pink-500/40 bg-gradient-to-br from-pink-500/20 to-rose-500/20 backdrop-blur-xl p-5 shadow-2xl shadow-pink-500/30 animate-in slide-in-from-bottom-4">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-pink-500 rounded-xl flex items-center justify-center flex-shrink-0 animate-pulse">
          <Bell className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <div className="font-bold mb-0.5">Time to take {rem.medication}</div>
          <div className="text-sm text-slate-300">{rem.dose} • Scheduled for {time}</div>
          {rem.notes && <div className="text-xs text-slate-400 mt-1 italic">{rem.notes}</div>}
          <div className="flex gap-2 mt-3">
            <button
              onClick={onTaken}
              className="flex-1 px-3 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-xs font-semibold transition flex items-center justify-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Mark Taken
            </button>
            <button
              onClick={onDismiss}
              className="px-3 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.1] text-xs font-semibold transition"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
