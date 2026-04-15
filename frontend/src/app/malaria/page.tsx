'use client'

import { useState } from 'react'
import { ArrowLeft, Upload, Activity } from 'lucide-react'
import dynamic from 'next/dynamic'
import { useToast } from '@/context/ToastContext'
import { useSession } from '@/context/SessionContext'
import { API_ENDPOINTS } from '@/lib/api-config'

// Dynamic imports for new components
const ProbabilityGauge = dynamic(() => import('@/components/ProbabilityGauge'), {
  ssr: false
})

const AIExplanation = dynamic(() => import('@/components/AIExplanation'), {
  ssr: false
})

export default function MalariaPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [prediction, setPrediction] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { addToast } = useToast()
  const { addSessionPrediction } = useSession()

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handlePredict = async () => {
    if (!selectedFile) {
      addToast('Please select an image file first', 'warning')
      return
    }

    setIsLoading(true)
    addToast('Analyzing blood smear image...', 'info', 3000)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      console.log('Sending request to backend...')
      const response = await fetch(`${API_ENDPOINTS.malaria}/predict`, {
        method: 'POST',
        body: formData,
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Server error:', errorText)
        throw new Error(`Server error: ${response.status} - ${errorText}`)
      }

      const result = await response.json()
      console.log('Prediction result:', result)
      
      setPrediction(result)
      addToast(`Analysis complete! ${result.prediction}`, 'success')
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Malaria',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          normalProbability: result.normal_probability,
          infectedProbability: result.infected_probability,
          parasiteDensity: result.parasite_density
        }
      }
      addSessionPrediction(predictionRecord)
    } catch (error) {
      console.error('Prediction error:', error)
      addToast(`Prediction failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Malaria Detection</h1>
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
            {/* Upload Section */}
            <div className="medical-card">
              <h2 className="text-2xl font-bold text-white mb-6">Upload Blood Smear</h2>
              <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label 
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center space-y-4"
                >
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <span className="text-gray-400">Click to upload blood smear image</span>
                  <span className="text-sm text-gray-500">
                    {selectedFile ? selectedFile.name : 'No file selected'}
                  </span>
                </label>
              </div>

              <button
                onClick={handlePredict}
                disabled={!selectedFile || isLoading}
                className="w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Malaria'}
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

                  {/* Modern Probability Gauges */}
                  <div className="grid grid-cols-2 gap-6 mt-6">
                    <div className="flex flex-col items-center">
                      <ProbabilityGauge 
                        value={prediction.normal_probability || 0}
                        size="md"
                        label="Normal"
                        type="normal"
                        animated={true}
                      />
                    </div>
                    <div className="flex flex-col items-center">
                      <ProbabilityGauge 
                        value={prediction.infected_probability || 0}
                        size="md"
                        label="Infected"
                        type="risk"
                        animated={true}
                      />
                    </div>
                  </div>

                  {/* GradCAM Visualization */}
                  {prediction.heatmap_url && (
                    <div className="mt-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-teal-400" />
                        AI Attention Visualization (GradCAM)
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-gray-400 text-sm mb-2">Original Image</p>
                          <img 
                            src={URL.createObjectURL(selectedFile!)} 
                            alt="Original" 
                            className="w-full rounded-lg"
                          />
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm mb-2">AI Attention Heatmap</p>
                          <img 
                            src={prediction.heatmap_url} 
                            alt="GradCAM Heatmap" 
                            className="w-full rounded-lg"
                          />
                        </div>
                      </div>
                      <p className="text-gray-400 text-sm mt-4">
                        The heatmap highlights regions the AI focused on to make its prediction. 
                        Red/yellow areas indicate high attention (potential parasite locations).
                      </p>
                    </div>
                  )}

                  {/* AI Explanation Component */}
                  <div className="mt-8">
                    <AIExplanation 
                      disease="Malaria Detection"
                      prediction={prediction.prediction}
                      confidence={prediction.confidence}
                      riskLevel={prediction.risk_level}
                      explanation={prediction.explanation}
                      riskFactors={[
                        {
                          name: 'Parasite Density',
                          impact: prediction.infected_probability > 70 ? 'high' : prediction.infected_probability > 40 ? 'medium' : 'low',
                          value: `${prediction.parasite_density || 'N/A'} parasites/μL`,
                          description: 'Higher density correlates with infection severity'
                        },
                        {
                          name: 'Image Quality',
                          impact: 'medium',
                          value: 'Good',
                          description: 'Clear blood smear image enables accurate detection'
                        }
                      ]}
                      recommendations={[
                        'Consult with a hematologist for confirmation',
                        'Consider follow-up blood tests',
                        'Monitor symptoms and seek immediate care if condition worsens'
                      ]}
                    />
                  </div>

                  {/* Parasite Density */}
                  {prediction.parasite_density && (
                    <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                      <h4 className="text-white font-semibold mb-2">Parasite Density</h4>
                      <p className="text-2xl text-yellow-400">{prediction.parasite_density}</p>
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
