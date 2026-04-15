'use client'

import { useState } from 'react'
import { ArrowLeft, Heart, Activity } from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

export default function HeartDiseasePage() {
  const [formData, setFormData] = useState({
    age: '',
    sex: '',
    cp: '',
    trestbps: '',
    chol: '',
    fbs: '',
    restecg: '',
    thalach: '',
    exang: '',
    oldpeak: '',
    slope: '',
    ca: '',
    thal: ''
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
      const response = await fetch(`${API_ENDPOINTS.heartDisease}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseFloat(formData.age) || 0,
          sex: parseFloat(formData.sex) || 0,
          cp: parseFloat(formData.cp) || 0,
          trestbps: parseFloat(formData.trestbps) || 0,
          chol: parseFloat(formData.chol) || 0,
          fbs: parseFloat(formData.fbs) || 0,
          restecg: parseFloat(formData.restecg) || 0,
          thalach: parseFloat(formData.thalach) || 0,
          exang: parseFloat(formData.exang) || 0,
          oldpeak: parseFloat(formData.oldpeak) || 0,
          slope: parseFloat(formData.slope) || 0,
          ca: parseFloat(formData.ca) || 0,
          thal: parseFloat(formData.thal) || 0
        }),
      })

      const result = await response.json()
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Heart Disease',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          diseaseProbability: result.disease_probability,
          healthyProbability: result.healthy_probability
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
    { id: 'age', label: 'Age', type: 'number', placeholder: 'Enter age (25-80)' },
    { id: 'sex', label: 'Sex', type: 'select', options: [
      { value: '1', label: 'Male' },
      { value: '0', label: 'Female' }
    ]},
    { id: 'cp', label: 'Chest Pain Type', type: 'select', options: [
      { value: '0', label: 'Typical angina' },
      { value: '1', label: 'Atypical angina' },
      { value: '2', label: 'Non-anginal pain' },
      { value: '3', label: 'Asymptomatic' }
    ]},
    { id: 'trestbps', label: 'Resting Blood Pressure', type: 'number', placeholder: 'Enter BP (mmHg)' },
    { id: 'chol', label: 'Serum Cholesterol', type: 'number', placeholder: 'Enter cholesterol (mg/dl)' },
    { id: 'fbs', label: 'Fasting Blood Sugar', type: 'select', options: [
      { value: '1', label: '> 120 mg/dl' },
      { value: '0', label: '<= 120 mg/dl' }
    ]},
    { id: 'restecg', label: 'Resting ECG', type: 'select', options: [
      { value: '0', label: 'Normal' },
      { value: '1', label: 'ST-T wave abnormality' },
      { value: '2', label: 'Left ventricular hypertrophy' }
    ]},
    { id: 'thalach', label: 'Max Heart Rate', type: 'number', placeholder: 'Enter max HR achieved' },
    { id: 'exang', label: 'Exercise Angina', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'oldpeak', label: 'ST Depression', type: 'number', placeholder: 'Enter ST depression' },
    { id: 'slope', label: 'ST Slope', type: 'select', options: [
      { value: '0', label: 'Upsloping' },
      { value: '1', label: 'Flat' },
      { value: '2', label: 'Downsloping' }
    ]},
    { id: 'ca', label: 'Major Vessels', type: 'select', options: [
      { value: '0', label: '0' },
      { value: '1', label: '1' },
      { value: '2', label: '2' },
      { value: '3', label: '3' }
    ]},
    { id: 'thal', label: 'Thalassemia', type: 'select', options: [
      { value: '1', label: 'Normal' },
      { value: '2', label: 'Fixed defect' },
      { value: '3', label: 'Reversible defect' }
    ]}
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Heart Disease Prediction</h1>
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
              <h2 className="text-2xl font-bold text-white mb-6">Cardiovascular Risk Factors</h2>
              <div className="space-y-4">
                {inputFields.map((field) => (
                  <div key={field.id}>
                    <label className="block text-white font-semibold mb-2">{field.label}</label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.id as keyof typeof formData]}
                        onChange={(e) => handleInputChange(field.id, e.target.value)}
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
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
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                      />
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={isLoading}
                className="w-full bg-red-500 text-white py-3 rounded-lg font-semibold hover:bg-red-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Heart Disease'}
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
                      <h4 className="text-white font-semibold mb-2">Heart Disease</h4>
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
