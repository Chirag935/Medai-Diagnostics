'use client'

import { useState } from 'react'
import { ArrowLeft, Activity } from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

export default function LiverDiseasePage() {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    total_bilirubin: '',
    direct_bilirubin: '',
    alkaline_phosphatase: '',
    alamine_aminotransferase: '',
    aspartate_aminotransferase: '',
    total_proteins: '',
    albumin: '',
    albumin_globulin_ratio: ''
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
      const response = await fetch(`${API_ENDPOINTS.liverDisease}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseFloat(formData.age) || 0,
          gender: parseFloat(formData.gender) || 0,
          total_bilirubin: parseFloat(formData.total_bilirubin) || 0,
          direct_bilirubin: parseFloat(formData.direct_bilirubin) || 0,
          alkaline_phosphatase: parseFloat(formData.alkaline_phosphatase) || 0,
          alamine_aminotransferase: parseFloat(formData.alamine_aminotransferase) || 0,
          aspartate_aminotransferase: parseFloat(formData.aspartate_aminotransferase) || 0,
          total_proteins: parseFloat(formData.total_proteins) || 0,
          albumin: parseFloat(formData.albumin) || 0,
          albumin_globulin_ratio: parseFloat(formData.albumin_globulin_ratio) || 0
        }),
      })

      const result = await response.json()
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Liver Disease',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          diseaseProbability: result.disease_probability,
          noDiseaseProbability: result.no_disease_probability
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
    { id: 'age', label: 'Age', type: 'number', placeholder: 'Enter age (18-90)' },
    { id: 'gender', label: 'Gender', type: 'select', options: [
      { value: '1', label: 'Male' },
      { value: '0', label: 'Female' }
    ]},
    { id: 'total_bilirubin', label: 'Total Bilirubin', type: 'number', placeholder: 'Enter total bilirubin (mg/dl)' },
    { id: 'direct_bilirubin', label: 'Direct Bilirubin', type: 'number', placeholder: 'Enter direct bilirubin (mg/dl)' },
    { id: 'alkaline_phosphatase', label: 'Alkaline Phosphatase', type: 'number', placeholder: 'Enter ALP (U/L)' },
    { id: 'alamine_aminotransferase', label: 'ALT (SGPT)', type: 'number', placeholder: 'Enter ALT level (U/L)' },
    { id: 'aspartate_aminotransferase', label: 'AST (SGOT)', type: 'number', placeholder: 'Enter AST level (U/L)' },
    { id: 'total_proteins', label: 'Total Proteins', type: 'number', placeholder: 'Enter total proteins (g/dl)' },
    { id: 'albumin', label: 'Albumin', type: 'number', placeholder: 'Enter albumin (g/dl)' },
    { id: 'albumin_globulin_ratio', label: 'Albumin/Globulin Ratio', type: 'number', placeholder: 'Enter A/G ratio' }
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Liver Disease Prediction</h1>
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
              <h2 className="text-2xl font-bold text-white mb-6">Liver Function Tests</h2>
              <div className="space-y-4">
                {inputFields.map((field) => (
                  <div key={field.id}>
                    <label className="block text-white font-semibold mb-2">{field.label}</label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.id as keyof typeof formData]}
                        onChange={(e) => handleInputChange(field.id, e.target.value)}
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
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
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
                      />
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={isLoading}
                className="w-full bg-orange-500 text-white py-3 rounded-lg font-semibold hover:bg-orange-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Liver Disease'}
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
                      <h4 className="text-white font-semibold mb-2">Healthy</h4>
                      <p className="text-2xl text-green-400">{prediction.healthy_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Liver Disease</h4>
                      <p className="text-2xl text-red-400">{prediction.disease_probability?.toFixed(1)}%</p>
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
