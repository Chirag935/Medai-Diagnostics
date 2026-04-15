'use client'

import { useState } from 'react'
import { ArrowLeft, Activity, Droplets } from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

export default function KidneyDiseasePage() {
  const [formData, setFormData] = useState({
    age: '',
    blood_pressure: '',
    specific_gravity: '',
    albumin: '',
    sugar: '',
    red_blood_cells: '',
    pus_cell: '',
    pus_cell_clumps: '',
    bacteria: '',
    blood_glucose_random: '',
    blood_urea: '',
    serum_creatinine: '',
    sodium: '',
    potassium: '',
    hemoglobin: '',
    packed_cell_volume: '',
    white_blood_cell_count: '',
    red_blood_cell_count: '',
    hypertension: '',
    diabetes_mellitus: '',
    coronary_artery_disease: '',
    appetite: '',
    pedema: '',
    anemia: ''
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
      const response = await fetch(`${API_ENDPOINTS.kidneyDisease}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseFloat(formData.age) || 0,
          blood_pressure: parseFloat(formData.blood_pressure) || 0,
          specific_gravity: parseFloat(formData.specific_gravity) || 0,
          albumin: parseFloat(formData.albumin) || 0,
          sugar: parseFloat(formData.sugar) || 0,
          red_blood_cells: parseFloat(formData.red_blood_cells) || 0,
          pus_cell: parseFloat(formData.pus_cell) || 0,
          pus_cell_clumps: parseFloat(formData.pus_cell_clumps) || 0,
          bacteria: parseFloat(formData.bacteria) || 0,
          blood_glucose_random: parseFloat(formData.blood_glucose_random) || 0,
          blood_urea: parseFloat(formData.blood_urea) || 0,
          serum_creatinine: parseFloat(formData.serum_creatinine) || 0,
          sodium: parseFloat(formData.sodium) || 0,
          potassium: parseFloat(formData.potassium) || 0,
          hemoglobin: parseFloat(formData.hemoglobin) || 0,
          packed_cell_volume: parseFloat(formData.packed_cell_volume) || 0,
          white_blood_cell_count: parseFloat(formData.white_blood_cell_count) || 0,
          red_blood_cell_count: parseFloat(formData.red_blood_cell_count) || 0,
          hypertension: parseFloat(formData.hypertension) || 0,
          diabetes_mellitus: parseFloat(formData.diabetes_mellitus) || 0,
          coronary_artery_disease: parseFloat(formData.coronary_artery_disease) || 0,
          appetite: parseFloat(formData.appetite) || 0,
          pedema: parseFloat(formData.pedema) || 0,
          anemia: parseFloat(formData.anemia) || 0
        }),
      })

      const result = await response.json()
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Kidney Disease',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          ckdProbability: result.ckd_probability,
          notCkdProbability: result.not_ckd_probability
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
    { id: 'blood_pressure', label: 'Blood Pressure', type: 'number', placeholder: 'Enter BP (mmHg)' },
    { id: 'specific_gravity', label: 'Specific Gravity', type: 'number', placeholder: 'Enter SG (1.0-1.05)' },
    { id: 'albumin', label: 'Albumin', type: 'number', placeholder: 'Enter albumin level' },
    { id: 'sugar', label: 'Sugar', type: 'number', placeholder: 'Enter sugar level' },
    { id: 'red_blood_cells', label: 'Red Blood Cells', type: 'select', options: [
      { value: '1', label: 'Normal' },
      { value: '0', label: 'Abnormal' }
    ]},
    { id: 'pus_cell', label: 'Pus Cell', type: 'select', options: [
      { value: '1', label: 'Normal' },
      { value: '0', label: 'Abnormal' }
    ]},
    { id: 'pus_cell_clumps', label: 'Pus Cell Clumps', type: 'select', options: [
      { value: '1', label: 'Present' },
      { value: '0', label: 'Absent' }
    ]},
    { id: 'bacteria', label: 'Bacteria', type: 'select', options: [
      { value: '1', label: 'Present' },
      { value: '0', label: 'Absent' }
    ]},
    { id: 'blood_glucose_random', label: 'Blood Glucose Random', type: 'number', placeholder: 'Enter glucose level' },
    { id: 'blood_urea', label: 'Blood Urea', type: 'number', placeholder: 'Enter blood urea level' },
    { id: 'serum_creatinine', label: 'Serum Creatinine', type: 'number', placeholder: 'Enter creatinine level' },
    { id: 'sodium', label: 'Sodium', type: 'number', placeholder: 'Enter sodium level' },
    { id: 'potassium', label: 'Potassium', type: 'number', placeholder: 'Enter potassium level' },
    { id: 'hemoglobin', label: 'Hemoglobin', type: 'number', placeholder: 'Enter hemoglobin level' },
    { id: 'packed_cell_volume', label: 'Packed Cell Volume', type: 'number', placeholder: 'Enter PCV' },
    { id: 'white_blood_cell_count', label: 'White Blood Cell Count', type: 'number', placeholder: 'Enter WBC count' },
    { id: 'red_blood_cell_count', label: 'Red Blood Cell Count', type: 'number', placeholder: 'Enter RBC count' },
    { id: 'hypertension', label: 'Hypertension', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'diabetes_mellitus', label: 'Diabetes Mellitus', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'coronary_artery_disease', label: 'Coronary Artery Disease', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'appetite', label: 'Appetite', type: 'select', options: [
      { value: '1', label: 'Good' },
      { value: '0', label: 'Poor' }
    ]},
    { id: 'pedema', label: 'Pedema', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]},
    { id: 'anemia', label: 'Anemia', type: 'select', options: [
      { value: '1', label: 'Yes' },
      { value: '0', label: 'No' }
    ]}
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-indigo-500 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Kidney Disease Prediction</h1>
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
              <h2 className="text-2xl font-bold text-white mb-6">Renal Function Assessment</h2>
              <div className="space-y-4">
                {inputFields.map((field) => (
                  <div key={field.id}>
                    <label className="block text-white font-semibold mb-2">{field.label}</label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.id as keyof typeof formData]}
                        onChange={(e) => handleInputChange(field.id, e.target.value)}
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
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
                        className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
                      />
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={isLoading}
                className="w-full bg-indigo-500 text-white py-3 rounded-lg font-semibold hover:bg-indigo-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Kidney Disease'}
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
                      <h4 className="text-white font-semibold mb-2">No CKD</h4>
                      <p className="text-2xl text-green-400">{prediction.no_ckd_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">CKD</h4>
                      <p className="text-2xl text-red-400">{prediction.ckd_probability?.toFixed(1)}%</p>
                    </div>
                  </div>

                  {/* CKD Stage */}
                  {prediction.ckd_stage && (
                    <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">CKD Stage</h4>
                      <p className="text-xl text-yellow-400">{prediction.ckd_stage}</p>
                    </div>
                  )}

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
