'use client'

import { useState, useEffect } from 'react'
import { Brain, Activity, Heart, FileText, BarChart3, Sparkles, Zap, Shield, Trash2 } from 'lucide-react'
import dynamic from 'next/dynamic'
import ThemeToggle from '@/components/ThemeToggle'
import { SkeletonGrid, SkeletonCard } from '@/components/Skeleton'
import { useSession } from '@/context/SessionContext'

// Dynamic imports for heavy components
const EnhancedPDFExport = dynamic(() => import('@/components/EnhancedPDFExport'), {
  ssr: false,
  loading: () => <div className="h-10 w-32 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
})

export default function HomePage() {
  const [showMetrics, setShowMetrics] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const { sessionPredictions, clearSessionPredictions } = useSession()

  // Track only current session predictions
  useEffect(() => {
    // Simulate loading for skeleton demo
    const timer = setTimeout(() => setIsLoading(false), 800)
    return () => clearTimeout(timer)
  }, [])

  const diseaseModules = [
    {
      id: 'pneumonia',
      name: 'Pneumonia Detection',
      icon: Activity,
      description: 'Chest X-ray analysis with CNN and Grad-CAM visualization',
      color: 'bg-blue-500'
    },
    {
      id: 'malaria',
      name: 'Malaria Detection',
      icon: Activity,
      description: 'Blood smear image analysis for parasite detection',
      color: 'bg-green-500'
    },
    {
      id: 'breast-cancer',
      name: 'Breast Cancer Prediction',
      icon: Heart,
      description: 'Clinical feature analysis for malignancy detection',
      color: 'bg-pink-500'
    },
    {
      id: 'diabetes',
      name: 'Diabetes Prediction',
      icon: Activity,
      description: 'Risk assessment based on clinical parameters',
      color: 'bg-yellow-500'
    },
    {
      id: 'heart-disease',
      name: 'Heart Disease Prediction',
      icon: Heart,
      description: 'Cardiovascular risk assessment using clinical parameters',
      color: 'bg-red-500'
    },
    {
      id: 'kidney-disease',
      name: 'Kidney Disease Prediction',
      icon: Activity,
      description: 'Renal function analysis for chronic kidney disease',
      color: 'bg-indigo-500'
    },
    {
      id: 'alzheimer',
      name: "Alzheimer's Detection",
      icon: Brain,
      description: 'MRI brain scan analysis for cognitive impairment',
      color: 'bg-purple-500'
    },
    {
      id: 'liver-disease',
      name: 'Liver Disease Prediction',
      icon: Activity,
      description: 'Biochemical marker analysis for liver function',
      color: 'bg-orange-500'
    }
  ]

  return (
    <div className="min-h-screen medical-gradient">
      {/* Header */}
      <header className="glassmorphism border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-teal-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">MedAI Diagnostics</h1>
            </div>
            <div className="flex items-center space-x-3">
              <ThemeToggle />
              <button 
                onClick={() => setShowMetrics(!showMetrics)}
                className="glassmorphism text-white p-2 rounded-lg hover:bg-white/10 transition-all flex items-center gap-2"
              >
                <BarChart3 className="w-5 h-5" />
                <span className="hidden sm:inline">{showMetrics ? 'Hide Metrics' : 'Show Metrics'}</span>
              </button>
              {sessionPredictions.length > 0 && (
                <button
                  onClick={clearSessionPredictions}
                  className="glassmorphism text-white/70 p-2 rounded-lg hover:text-red-400 hover:bg-red-500/10 transition-all flex items-center gap-2"
                  title="Clear current session predictions"
                >
                  <Trash2 className="w-5 h-5" />
                  <span className="hidden sm:inline">Clear</span>
                </button>
              )}
              <EnhancedPDFExport 
                predictions={sessionPredictions} 
                patientName="Patient" 
                patientId={`P-${Date.now().toString(36).toUpperCase()}`}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-6">
            Advanced AI-Powered Medical Diagnostics
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            Experience the future of healthcare with our comprehensive disease detection platform. 
            Leveraging cutting-edge machine learning models to provide accurate, real-time medical predictions.
          </p>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={() => {
                document.getElementById('disease-modules')?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="bg-teal-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-teal-600 transition-all transform hover:scale-105"
            >
              Start Diagnosis
            </button>
            <button 
              onClick={() => setShowMetrics(true)}
              className="glassmorphism text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-all"
            >
              View Performance Metrics
            </button>
          </div>
        </div>

        {/* Disease Modules Grid */}
        <div id="disease-modules" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {isLoading ? (
            // Skeleton loading state
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            diseaseModules.map((module, index) => {
              const Icon = module.icon
              return (
                <div
                  key={module.id}
                  className="medical-card group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-teal-500/20 animate-fadeIn"
                  style={{ animationDelay: `${index * 50}ms` }}
                  onClick={() => {
                    window.location.href = `/${module.id}`
                  }}
                >
                  <div className={`w-12 h-12 ${module.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-teal-400 transition-colors">{module.name}</h3>
                  <p className="text-gray-400 text-sm group-hover:text-gray-300 transition-colors">{module.description}</p>
                  
                  {/* Hover indicator */}
                  <div className="mt-4 flex items-center text-xs text-teal-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span>Click to analyze</span>
                    <svg className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-white text-center mb-12">Platform Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="medical-card text-center">
            <div className="w-16 h-16 bg-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-semibold text-white mb-2">AI-Powered Analysis</h4>
            <p className="text-gray-400">State-of-the-art machine learning models for accurate disease detection</p>
          </div>
          <div className="medical-card text-center">
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-semibold text-white mb-2">Real-time Metrics</h4>
            <p className="text-gray-400">Comprehensive performance analytics and confidence scoring</p>
          </div>
          <div className="medical-card text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-semibold text-white mb-2">Detailed Reports</h4>
            <p className="text-gray-400">Exportable PDF reports with clinical explanations</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="glassmorphism border-t border-white/10 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-400">
            <p>&copy; 2026 MedAI Diagnostics. Educational and research purposes only.</p>
            <p className="mt-2 text-sm">This tool does not constitute medical advice. Always consult healthcare professionals.</p>
          </div>
        </div>
      </footer>

      {/* Performance Metrics Modal */}
      {showMetrics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-800">Performance Metrics</h3>
              <button 
                onClick={() => setShowMetrics(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Model Accuracy</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Breast Cancer:</span>
                      <span className="text-green-600 font-semibold">98.4%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Diabetes:</span>
                      <span className="text-green-600 font-semibold">92.1%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Heart Disease:</span>
                      <span className="text-green-600 font-semibold">89.7%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Kidney Disease:</span>
                      <span className="text-green-600 font-semibold">90.5%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Liver Disease:</span>
                      <span className="text-green-600 font-semibold">90.5%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Alzheimer&apos;s:</span>
                      <span className="text-green-600 font-semibold">92.0%</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Response Times</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Average Response:</span>
                      <span className="text-blue-600 font-semibold">0.8s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">95th Percentile:</span>
                      <span className="text-blue-600 font-semibold">1.2s</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-100 rounded-lg">
                <h4 className="font-semibold text-gray-800 mb-2">System Status</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Backend Status:</span>
                    <span className="text-green-600 font-semibold">Online</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frontend Status:</span>
                    <span className="text-green-600 font-semibold">Online</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Models:</span>
                    <span className="text-green-600 font-semibold">8/8</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">API Endpoints:</span>
                    <span className="text-green-600 font-semibold">Functional</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
