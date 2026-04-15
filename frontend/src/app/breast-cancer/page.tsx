'use client'

import { useState } from 'react'
import { ArrowLeft, Heart, Activity } from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

export default function BreastCancerPage() {
  const [formData, setFormData] = useState({
    radius_mean: '',
    texture_mean: '',
    perimeter_mean: '',
    area_mean: '',
    smoothness_mean: '',
    compactness_mean: '',
    concavity_mean: '',
    concave_points_mean: '',
    symmetry_mean: '',
    fractal_dimension_mean: '',
    radius_se: '',
    texture_se: '',
    perimeter_se: '',
    area_se: '',
    smoothness_se: '',
    compactness_se: '',
    concavity_se: '',
    concave_points_se: '',
    symmetry_se: '',
    fractal_dimension_se: '',
    radius_worst: '',
    texture_worst: '',
    perimeter_worst: '',
    area_worst: '',
    smoothness_worst: '',
    compactness_worst: '',
    concavity_worst: '',
    concave_points_worst: '',
    symmetry_worst: '',
    fractal_dimension_worst: ''
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
      const response = await fetch(`${API_ENDPOINTS.breastCancer}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          radius_mean: parseFloat(formData.radius_mean) || 0,
          texture_mean: parseFloat(formData.texture_mean) || 0,
          perimeter_mean: parseFloat(formData.perimeter_mean) || 0,
          area_mean: parseFloat(formData.area_mean) || 0,
          smoothness_mean: parseFloat(formData.smoothness_mean) || 0,
          compactness_mean: parseFloat(formData.compactness_mean) || 0,
          concavity_mean: parseFloat(formData.concavity_mean) || 0,
          concave_points_mean: parseFloat(formData.concave_points_mean) || 0,
          symmetry_mean: parseFloat(formData.symmetry_mean) || 0,
          fractal_dimension_mean: parseFloat(formData.fractal_dimension_mean) || 0,
          radius_se: parseFloat(formData.radius_se) || 0,
          texture_se: parseFloat(formData.texture_se) || 0,
          perimeter_se: parseFloat(formData.perimeter_se) || 0,
          area_se: parseFloat(formData.area_se) || 0,
          smoothness_se: parseFloat(formData.smoothness_se) || 0,
          compactness_se: parseFloat(formData.compactness_se) || 0,
          concavity_se: parseFloat(formData.concavity_se) || 0,
          concave_points_se: parseFloat(formData.concave_points_se) || 0,
          symmetry_se: parseFloat(formData.symmetry_se) || 0,
          fractal_dimension_se: parseFloat(formData.fractal_dimension_se) || 0,
          radius_worst: parseFloat(formData.radius_worst) || 0,
          texture_worst: parseFloat(formData.texture_worst) || 0,
          perimeter_worst: parseFloat(formData.perimeter_worst) || 0,
          area_worst: parseFloat(formData.area_worst) || 0,
          smoothness_worst: parseFloat(formData.smoothness_worst) || 0,
          compactness_worst: parseFloat(formData.compactness_worst) || 0,
          concavity_worst: parseFloat(formData.concavity_worst) || 0,
          concave_points_worst: parseFloat(formData.concave_points_worst) || 0,
          symmetry_worst: parseFloat(formData.symmetry_worst) || 0,
          fractal_dimension_worst: parseFloat(formData.fractal_dimension_worst) || 0
        }),
      })

      const result = await response.json()
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Breast Cancer',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          benignProbability: result.benign_probability,
          malignantProbability: result.malignant_probability
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
    { id: 'radius_mean', label: 'Radius Mean', type: 'number', placeholder: 'Enter radius mean' },
    { id: 'texture_mean', label: 'Texture Mean', type: 'number', placeholder: 'Enter texture mean' },
    { id: 'perimeter_mean', label: 'Perimeter Mean', type: 'number', placeholder: 'Enter perimeter mean' },
    { id: 'area_mean', label: 'Area Mean', type: 'number', placeholder: 'Enter area mean' },
    { id: 'smoothness_mean', label: 'Smoothness Mean', type: 'number', placeholder: 'Enter smoothness mean' },
    { id: 'compactness_mean', label: 'Compactness Mean', type: 'number', placeholder: 'Enter compactness mean' },
    { id: 'concavity_mean', label: 'Concavity Mean', type: 'number', placeholder: 'Enter concavity mean' },
    { id: 'concave_points_mean', label: 'Concave Points Mean', type: 'number', placeholder: 'Enter concave points mean' },
    { id: 'symmetry_mean', label: 'Symmetry Mean', type: 'number', placeholder: 'Enter symmetry mean' },
    { id: 'fractal_dimension_mean', label: 'Fractal Dimension Mean', type: 'number', placeholder: 'Enter fractal dimension mean' },
    { id: 'radius_se', label: 'Radius SE', type: 'number', placeholder: 'Enter radius SE' },
    { id: 'texture_se', label: 'Texture SE', type: 'number', placeholder: 'Enter texture SE' },
    { id: 'perimeter_se', label: 'Perimeter SE', type: 'number', placeholder: 'Enter perimeter SE' },
    { id: 'area_se', label: 'Area SE', type: 'number', placeholder: 'Enter area SE' },
    { id: 'smoothness_se', label: 'Smoothness SE', type: 'number', placeholder: 'Enter smoothness SE' },
    { id: 'compactness_se', label: 'Compactness SE', type: 'number', placeholder: 'Enter compactness SE' },
    { id: 'concavity_se', label: 'Concavity SE', type: 'number', placeholder: 'Enter concavity SE' },
    { id: 'concave_points_se', label: 'Concave Points SE', type: 'number', placeholder: 'Enter concave points SE' },
    { id: 'symmetry_se', label: 'Symmetry SE', type: 'number', placeholder: 'Enter symmetry SE' },
    { id: 'fractal_dimension_se', label: 'Fractal Dimension SE', type: 'number', placeholder: 'Enter fractal dimension SE' },
    { id: 'radius_worst', label: 'Radius Worst', type: 'number', placeholder: 'Enter radius worst' },
    { id: 'texture_worst', label: 'Texture Worst', type: 'number', placeholder: 'Enter texture worst' },
    { id: 'perimeter_worst', label: 'Perimeter Worst', type: 'number', placeholder: 'Enter perimeter worst' },
    { id: 'area_worst', label: 'Area Worst', type: 'number', placeholder: 'Enter area worst' },
    { id: 'smoothness_worst', label: 'Smoothness Worst', type: 'number', placeholder: 'Enter smoothness worst' },
    { id: 'compactness_worst', label: 'Compactness Worst', type: 'number', placeholder: 'Enter compactness worst' },
    { id: 'concavity_worst', label: 'Concavity Worst', type: 'number', placeholder: 'Enter concavity worst' },
    { id: 'concave_points_worst', label: 'Concave Points Worst', type: 'number', placeholder: 'Enter concave points worst' },
    { id: 'symmetry_worst', label: 'Symmetry Worst', type: 'number', placeholder: 'Enter symmetry worst' },
    { id: 'fractal_dimension_worst', label: 'Fractal Dimension Worst', type: 'number', placeholder: 'Enter fractal dimension worst' }
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-pink-500 rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Breast Cancer Prediction</h1>
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
              <h2 className="text-2xl font-bold text-white mb-6">Cell Nuclei Measurements</h2>
              <div className="grid grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                {inputFields.map((field) => (
                  <div key={field.id}>
                    <label className="block text-white font-semibold mb-2 text-sm">{field.label}</label>
                    <input
                      type={field.type}
                      value={formData[field.id as keyof typeof formData]}
                      onChange={(e) => handleInputChange(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full p-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-pink-500 focus:ring-2 focus:ring-pink-500 text-sm"
                    />
                  </div>
                ))}
              </div>

              <button
                onClick={handlePredict}
                disabled={isLoading}
                className="w-full bg-pink-500 text-white py-3 rounded-lg font-semibold hover:bg-pink-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all mt-6"
              >
                {isLoading ? 'Analyzing...' : 'Predict Breast Cancer'}
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
                      <h4 className="text-white font-semibold mb-2">Benign</h4>
                      <p className="text-2xl text-green-400">{prediction.benign_probability?.toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Malignant</h4>
                      <p className="text-2xl text-red-400">{prediction.malignant_probability?.toFixed(1)}%</p>
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
