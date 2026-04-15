'use client'

import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

interface ProbabilityGaugeProps {
  value: number
  max?: number
  size?: 'sm' | 'md' | 'lg' | 'xl'
  label?: string
  sublabel?: string
  type?: 'confidence' | 'risk' | 'normal'
  showValue?: boolean
  animated?: boolean
}

const sizes = {
  sm: { width: 80, strokeWidth: 6, fontSize: 16 },
  md: { width: 120, strokeWidth: 8, fontSize: 24 },
  lg: { width: 160, strokeWidth: 10, fontSize: 32 },
  xl: { width: 200, strokeWidth: 12, fontSize: 40 }
}

export default function ProbabilityGauge({
  value,
  max = 100,
  size = 'md',
  label,
  sublabel,
  type = 'confidence',
  showValue = true,
  animated = true
}: ProbabilityGaugeProps) {
  const [animatedValue, setAnimatedValue] = useState(0)
  
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const { width, strokeWidth, fontSize } = sizes[size]
  const radius = (width - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedValue / 100) * circumference
  
  useEffect(() => {
    if (animated) {
      const duration = 1500
      const startTime = Date.now()
      const startValue = 0
      
      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / duration, 1)
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4)
        const currentValue = startValue + (percentage - startValue) * easeOutQuart
        
        setAnimatedValue(currentValue)
        
        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }
      
      requestAnimationFrame(animate)
    } else {
      setAnimatedValue(percentage)
    }
  }, [percentage, animated])

  const getColor = () => {
    if (type === 'risk') {
      if (percentage >= 70) return '#ef4444' // red-500
      if (percentage >= 40) return '#f59e0b' // amber-500
      return '#22c55e' // green-500
    }
    if (type === 'normal') {
      return '#22c55e' // green-500
    }
    // confidence
    if (percentage >= 80) return '#22c55e' // green-500
    if (percentage >= 60) return '#3b82f6' // blue-500
    if (percentage >= 40) return '#f59e0b' // amber-500
    return '#ef4444' // red-500
  }

  const getGradient = () => {
    const color = getColor()
    return `conic-gradient(from 180deg, ${color}33, ${color})`
  }

  const color = getColor()

  return (
    <div className={cn('flex flex-col items-center', size === 'sm' ? 'gap-1' : 'gap-2')}>
      <div className="relative" style={{ width, height: width }}>
        {/* Background circle */}
        <svg
          className="transform -rotate-90"
          width={width}
          height={width}
        >
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200 dark:text-gray-700"
          />
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-300"
            style={{
              filter: `drop-shadow(0 0 ${strokeWidth / 2}px ${color}50)`
            }}
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {showValue && (
            <span
              className="font-bold text-gray-800 dark:text-white tabular-nums"
              style={{ fontSize }}
            >
              {animatedValue.toFixed(1)}%
            </span>
          )}
        </div>
        
        {/* Glow effect */}
        <div
          className="absolute inset-0 rounded-full opacity-30 blur-xl"
          style={{
            background: getGradient()
          }}
        />
      </div>
      
      {label && (
        <p className={cn(
          'font-semibold text-center text-gray-700 dark:text-gray-300',
          size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
        )}>
          {label}
        </p>
      )}
      
      {sublabel && (
        <p className={cn(
          'text-center text-gray-500 dark:text-gray-400',
          size === 'sm' ? 'text-[10px]' : 'text-xs'
        )}>
          {sublabel}
        </p>
      )}
    </div>
  )
}

// Mini version for compact displays
export function MiniGauge({ 
  value, 
  type = 'confidence',
  size = 40 
}: { 
  value: number
  type?: 'confidence' | 'risk' | 'normal'
  size?: number
}) {
  const percentage = Math.min(Math.max(value, 0), 100)
  const strokeWidth = size / 10
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getColor = () => {
    if (type === 'risk') {
      if (percentage >= 70) return '#ef4444'
      if (percentage >= 40) return '#f59e0b'
      return '#22c55e'
    }
    if (percentage >= 80) return '#22c55e'
    if (percentage >= 60) return '#3b82f6'
    if (percentage >= 40) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-200 dark:text-gray-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[10px] font-bold text-gray-700 dark:text-gray-300">
          {Math.round(percentage)}%
        </span>
      </div>
    </div>
  )
}
