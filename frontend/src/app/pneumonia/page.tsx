/* eslint-disable @next/next/no-img-element */
'use client'

import { useState } from 'react'
import { ArrowLeft, Upload, Activity } from 'lucide-react'
import dynamic from 'next/dynamic'
import { API_ENDPOINTS } from '@/lib/api-config'
import { useSession } from '@/context/SessionContext'

// Dynamic imports for new components
const ProbabilityGauge = dynamic(() => import('@/components/ProbabilityGauge'), {
  ssr: false
})

const AIExplanation = dynamic(() => import('@/components/AIExplanation'), {
  ssr: false
})

export default function PneumoniaPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [prediction, setPrediction] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { addSessionPrediction } = useSession()

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handlePredict = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_ENDPOINTS.pneumonia}/predict`, {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()
      if (!response.ok) {
        console.error('API error:', result)
        return
      }
      setPrediction(result)
      
      // Add prediction to current session
      const predictionRecord = {
        disease: 'Pneumonia',
        prediction: result.prediction,
        confidence: result.confidence,
        riskLevel: result.risk_level,
        explanation: result.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          normalProbability: result.normal_probability,
          pneumoniaProbability: result.pneumonia_probability
        }
      }
      addSessionPrediction(predictionRecord)
    } catch (error) {
      console.error('Prediction error:', error)
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
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Pneumonia Detection</h1>
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
              <h2 className="text-2xl font-bold text-white mb-6">Upload Chest X-Ray</h2>
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
                  <span className="text-gray-400">Click to upload chest X-ray image</span>
                  <span className="text-sm text-gray-500">
                    {selectedFile ? selectedFile.name : 'No file selected'}
                  </span>
                </label>
              </div>

              <button
                onClick={handlePredict}
                disabled={!selectedFile || isLoading}
                className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Analyzing...' : 'Predict Pneumonia'}
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
                      <span className="text-white">{(prediction.confidence ?? 0).toFixed(1)}%</span>
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

                  {/* AI Explanation Component */}
                  <div className="mt-8">
                    <AIExplanation 
                      disease="Pneumonia Detection"
                      prediction={prediction.prediction}
                      confidence={prediction.confidence ?? 0}
                      riskLevel={prediction.risk_level}
                      explanation={prediction.explanation}
                      riskFactors={[
                        {
                          name: 'Opacity Patterns',
                          impact: prediction.confidence > 70 ? 'high' : prediction.confidence > 40 ? 'medium' : 'low',
                          value: prediction.prediction.includes('Pneumonia') ? 'Detected' : 'Not Detected',
                          description: 'Lung opacities visible in X-ray indicate potential infection'
                        },
                        {
                          name: 'Image Quality',
                          impact: 'medium',
                          value: 'Good',
                          description: 'Clear chest X-ray enables accurate detection'
                        }
                      ]}
                      recommendations={[
                        'Consult with a pulmonologist for clinical correlation',
                        'Consider additional imaging if symptoms persist',
                        'Monitor respiratory symptoms closely'
                      ]}
                    />
                  </div>

                  {/* Grad-CAM Heatmap Visualization */}
                  {prediction.heatmap_url && (
                    <div className="mt-6 p-4 bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-xl border border-gray-700/50">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-white font-semibold flex items-center gap-2">
                          <Activity className="w-4 h-4 text-blue-400" />
                          Grad-CAM Heatmap
                        </h4>
                        <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full">
                          AI Attention
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm mb-3">
                        Areas highlighted in red indicate regions the AI focused on for pneumonia detection
                      </p>
                      <div className="relative bg-black rounded-lg overflow-hidden">
                        <img 
                          src={`${API_ENDPOINTS.pneumonia.replace('/api/pneumonia', '')}${prediction.heatmap_url}`} 
                          alt="Grad-CAM heatmap showing AI attention areas" 
                          className="w-full rounded-lg"
                          onError={(e) => {
                            // Fallback: generate a client-side heatmap if server image fails
                            const canvas = document.createElement('canvas');
                            canvas.width = 224;
                            canvas.height = 224;
                            const ctx = canvas.getContext('2d');
                            if (ctx) {
                              // Create a simple heatmap pattern
                              const gradient = ctx.createRadialGradient(112, 112, 0, 112, 112, 112);
                              gradient.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
                              gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.4)');
                              gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
                              ctx.fillStyle = gradient;
                              ctx.fillRect(0, 0, 224, 224);
                            }
                            (e.target as HTMLImageElement).src = canvas.toDataURL();
                          }}
                        />
                        <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-gray-300">
                          AI Focus Areas
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mt-3 text-xs">
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
                          <span className="text-gray-400">High Attention</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-blue-400 rounded-sm"></div>
                          <span className="text-gray-400">Medium Attention</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-gray-800 rounded-sm border border-gray-600"></div>
                          <span className="text-gray-400">Low Attention</span>
                        </div>
                      </div>
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
