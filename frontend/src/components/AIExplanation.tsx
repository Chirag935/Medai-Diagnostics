'use client'

import { useState } from 'react'
import { Brain, HelpCircle, ChevronDown, ChevronUp, AlertTriangle, Info, Lightbulb } from 'lucide-react'
import { cn } from '@/lib/utils'

interface RiskFactor {
  name: string
  impact: 'high' | 'medium' | 'low'
  value: string
  description: string
}

interface AIExplanationProps {
  disease: string
  prediction: string
  confidence: number
  riskLevel: string
  explanation: string
  riskFactors?: RiskFactor[]
  recommendations?: string[]
}

export default function AIExplanation({
  disease,
  prediction,
  confidence,
  riskLevel,
  explanation,
  riskFactors = [],
  recommendations = []
}: AIExplanationProps) {
  const [showDetails, setShowDetails] = useState(false)
  const [showFactors, setShowFactors] = useState(false)
  const [showRecommendations, setShowRecommendations] = useState(false)

  const getNaturalLanguageSummary = () => {
    const confidenceText = confidence >= 80 ? 'high confidence' : confidence >= 60 ? 'moderate confidence' : 'low confidence'
    const detected = prediction.toLowerCase().includes('detected') || prediction.toLowerCase().includes('positive') || prediction.toLowerCase().includes('disease')
    
    if (detected) {
      return `The AI model has detected **${prediction}** with **${confidenceText}** (${confidence.toFixed(1)}%). Based on the analysis of your input data, the model has identified patterns that are consistent with this condition.`
    } else {
      return `The AI model predicts **${prediction}** with **${confidenceText}** (${confidence.toFixed(1)}%). The analysis indicates a lower likelihood of disease presence based on the patterns in your data.`
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-500 bg-red-50 dark:bg-red-900/20 border-red-200'
      case 'medium':
        return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200'
      case 'low':
        return 'text-green-500 bg-green-50 dark:bg-green-900/20 border-green-200'
      default:
        return 'text-gray-500 bg-gray-50 dark:bg-gray-800 border-gray-200'
    }
  }

  return (
    <div className="space-y-4">
      {/* AI Summary Card */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-5 border border-purple-200 dark:border-purple-800">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800 dark:text-white mb-1">
              AI Analysis Summary
            </h3>
            <p 
              className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: getNaturalLanguageSummary().replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-600 dark:text-purple-400">$1</strong>') 
              }}
            />
          </div>
        </div>
      </div>

      {/* Why this prediction? */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-blue-500" />
            <span className="font-medium text-gray-800 dark:text-white">
              Why did the AI predict this?
            </span>
          </div>
          {showDetails ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>
        
        {showDetails && (
          <div className="px-4 pb-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                {explanation || `The machine learning model analyzed your input data using patterns learned from thousands of previous cases. The ${confidence.toFixed(1)}% confidence score indicates how certain the model is about this prediction based on the similarity of your data to known cases.`}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Risk Factors */}
      {riskFactors.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            onClick={() => setShowFactors(!showFactors)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              <span className="font-medium text-gray-800 dark:text-white">
                Key Risk Factors
              </span>
              <span className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full text-gray-600 dark:text-gray-400">
                {riskFactors.length}
              </span>
            </div>
            {showFactors ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {showFactors && (
            <div className="px-4 pb-4 space-y-2">
              {riskFactors.map((factor, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex items-start gap-3 p-3 rounded-lg border transition-all hover:shadow-sm cursor-pointer group',
                    getImpactColor(factor.impact)
                  )}
                >
                  <div className={cn(
                    'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                    factor.impact === 'high' ? 'bg-red-500' :
                    factor.impact === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  )} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{factor.name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-white dark:bg-gray-800">
                        {factor.value}
                      </span>
                    </div>
                    <p className="text-xs mt-1 opacity-80">
                      {factor.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            onClick={() => setShowRecommendations(!showRecommendations)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              <span className="font-medium text-gray-800 dark:text-white">
                Recommendations
              </span>
            </div>
            {showRecommendations ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {showRecommendations && (
            <div className="px-4 pb-4">
              <ul className="space-y-2">
                {recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <span className="text-green-500 mt-0.5">✓</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Disclaimer */}
      <div className="flex items-start gap-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <p>
          This AI analysis is for informational purposes only and should not be considered as medical advice. 
          Always consult with qualified healthcare professionals for proper diagnosis and treatment.
        </p>
      </div>
    </div>
  )
}
