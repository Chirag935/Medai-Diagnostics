'use client'

import { useState } from 'react'
import { API_BASE_URL } from '@/lib/api-config'

export default function ApiTest() {
  const [status, setStatus] = useState<string>('Click to test API')
  const [loading, setLoading] = useState(false)

  const testConnection = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      const data = await response.json()
      setStatus(`✅ API Connected! Status: ${JSON.stringify(data)}`)
    } catch (error) {
      setStatus(`❌ API Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <h3 className="font-bold mb-2">API Connection Test</h3>
      <p className="text-sm mb-2">Backend URL: {API_BASE_URL}</p>
      <button
        onClick={testConnection}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>
      <p className="mt-2 text-sm">{status}</p>
    </div>
  )
}
