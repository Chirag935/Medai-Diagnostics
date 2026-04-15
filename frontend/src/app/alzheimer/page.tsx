'use client'

import { useState } from 'react'
import { ArrowLeft, Brain, Activity } from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

export default function AlzheimerPage() {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    education_years: '',
    mmse_score: '',
    memory_complaints: '',
    behavioral_problems: '',
    adl_score: '',
    functional_assessment: '',
    brain_volume_ratio: '',
    cortical_thickness: '',
    csf_protein_level: '',
    hippocampal_atrophy: ''
  })
  const [prediction, setPrediction] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { addSessionPrediction } = useSession()

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handlePredict = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_ENDPOINTS.alzheimer}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseFloat(formData.age) || 0,
          gender: parseFloat(formData.gender) || 0,
          education_years: parseFloat(formData.education_years) || 0,
          mmse_score: parseFloat(formData.mmse_score) || 0,
          memory_complaints: parseFloat(formData.memory_complaints) || 0,
          behavioral_problems: parseFloat(formData.behavioral_problems) || 0,
          adl_score: parseFloat(formData.adl_score) || 0,
          functional_assessment: parseFloat(formData.functional_assessment) || 0,
          brain_volume_ratio: parseFloat(formData.brain_volume_ratio) || 0,
          cortical_thickness: parseFloat(formData.cortical_thickness) || 0,
          csf_protein_level: parseFloat(formData.csf_protein_level) || 0,
          hippocampal_atrophy: parseFloat(formData.hippocampal_atrophy) || 0
        }),
      })

      const result = await response.json()
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Alzheimer',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          alzheimerProbability: result.alzheimer_probability,
          noAlzheimerProbability: result.no_alzheimer_probability
        },
        inputs: formData
      }
      addSessionPrediction(predictionRecord)
    } catch (error) {
      console.error('Prediction error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const inputFields = [
    { id: 'age', label: 'Age', type: 'number', placeholder: 'Enter age (45-90)' },
    { id: 'gender', label: 'Gender', type: 'select', options: [
      { value: '1', label: 'Male' },
      { value: '0', label: 'Female' }
    ]},
    { id: 'education_years', label: 'Education Years', type: 'number', placeholder: 'Years of education' },
    { id: 'mmse_score', label: 'MMSE Score', type: 'number', placeholder: 'Mini-Mental State Exam (0-30)' },
    { id: 'memory_complaints', label: 'Memory Complaints', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'behavioral_problems', label: 'Behavioral Problems', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'adl_score', label: 'ADL Score', type: 'number', placeholder: 'Activities of Daily Living (0-20)' },
    { id: 'functional_assessment', label: 'Functional Assessment', type: 'number', placeholder: 'Functional assessment score' },
    { id: 'brain_volume_ratio', label: 'Brain Volume Ratio', type: 'number', placeholder: 'Brain volume ratio (0.5-1.5)' },
    { id: 'cortical_thickness', label: 'Cortical Thickness', type: 'number', placeholder: 'Cortical thickness (1.5-4.5)' },
    { id: 'csf_protein_level', label: 'CSF Protein Level', type: 'number', placeholder: 'CSF protein level (0.5-3.0)' },
    { id: 'hippocampal_atrophy', label: 'Hippocampal Atrophy', type: 'number', placeholder: 'Hippocampal atrophy score (0.0-1.0)' }
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Alzheimer's Prediction</h1>
            </div>
            <button 
              onClick={() => window.history.back()}
              className="glassmorphism text-white px-4 py-2 rounded-lg hover:bg-white/10 transition-all"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <div className="medical-card">
              <h2 className="text-2xl font-bold text-white mb-6">Cognitive Assessment</h2>
              <div className="space-y-4">
                {inputFields.map((field) => (
                  <div key={field.id}>
                    <label className="block text-white font-semibold mb-2">{field.label}</label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.id as keyof typeof formData]}
                        onChange={(e) => handleInputChange(field.id, e.target.value)}
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="">Select...</option>
                        {field.options?.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type}
                        value={formData[field.id as keyof typeof formData]}
                        onChange={(e) => handleInputChange(field.id, e.target.value)}
                        placeholder={field.placeholder}
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500"
                      />
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={isLoading}
                className="w-full bg-purple-500 text-white py-3 rounded-lg font-semibold hover:bg-purple-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Alzheimer\'s'}
              </button>
            </div>

            {/* Results Section */}
            {prediction && (
              <div className="medical-card">
                <h2 className="text-2xl font-bold text-white mb-6">Analysis Results</h2>
                
                <div className="space-y-4">
                  {/* Prediction Result */}
                  <div className={`p-4 rounded-lg ${
                    prediction.risk_level === 'LOW' ? 'bg-green-500/20 border-green-500' :
                    prediction.risk_level === 'MODERATE' ? 'bg-yellow-500/20 border-yellow-500' :
                    prediction.risk_level === 'HIGH' ? 'bg-orange-500/20 border-orange-500' :
                    'bg-red-500/20 border-red-500'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-semibold">Prediction:</span>
                      <span className="text-white">{prediction.prediction}</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-semibold">Confidence:</span>
                      <span className="text-white">{prediction.confidence.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white font-semibold">Risk Level:</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        prediction.risk_level === 'LOW' ? 'bg-green-500' :
                        prediction.risk_level === 'MODERATE' ? 'bg-yellow-500' :
                        prediction.risk_level === 'HIGH' ? 'bg-orange-500' :
                        'bg-red-500'
                      } text-white`}>
                        {prediction.risk_level}
                      </span>
                    </div>
                  </div>

                  {/* Probabilities */}
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Non-Demented</h4>
                      <p className="text-2xl text-green-400">{prediction.non_demented_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Mild/Moderate</h4>
                      <p className="text-2xl text-yellow-400">
                        {((prediction.very_mild_probability || 0) + (prediction.mild_probability || 0) + (prediction.moderate_probability || 0)).toFixed(1)}%
                      </p>
                    </div>
                  </div>

                  {/* Detailed Probabilities */}
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Very Mild</h4>
                      <p className="text-xl text-blue-400">{prediction.very_mild_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Mild</h4>
                      <p className="text-xl text-yellow-400">{prediction.mild_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Moderate</h4>
                      <p className="text-xl text-orange-400">{prediction.moderate_probability?.toFixed(1)}%</p>
                    </div>
                  </div>

                  {/* Explanation */}
                  <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                    <h4 className="text-white font-semibold mb-2">Clinical Explanation</h4>
                    <p className="text-gray-300">{prediction.explanation}</p>
                  </div>

                  {/* Risk Factors */}
                  {prediction.top_risk_factors && prediction.top_risk_factors.length > 0 && (
                    <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Top Risk Factors</h4>
                      <ul className="space-y-2">
                        {prediction.top_risk_factors.map((factor: string, index: number) => (
                          <li key={index} className="text-yellow-400">• {factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
