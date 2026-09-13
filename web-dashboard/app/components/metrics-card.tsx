
"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { 
  Users, 
  DollarSign, 
  Target, 
  TrendingUp, 
  Brain, 
  Star,
  Clock,
  BarChart3
} from 'lucide-react'

const iconMap = {
  Users,
  DollarSign,
  Target,
  TrendingUp,
  Brain,
  Star,
  Clock,
  BarChart3
}

interface MetricsCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  iconName: keyof typeof iconMap
  description?: string
  delay?: number
}

export default function MetricsCard({ 
  title, 
  value, 
  change, 
  changeType = 'neutral', 
  iconName, 
  description,
  delay = 0 
}: MetricsCardProps) {
  const Icon = iconMap[iconName]
  const [displayValue, setDisplayValue] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
      
      // Animate the number if it's numeric
      if (typeof value === 'number') {
        let start = 0
        const end = value
        const duration = 1000
        const increment = end / (duration / 16)
        
        const counter = setInterval(() => {
          start += increment
          if (start >= end) {
            setDisplayValue(end)
            clearInterval(counter)
          } else {
            setDisplayValue(Math.floor(start))
          }
        }, 16)
        
        return () => clearInterval(counter)
      }
    }, delay)

    return () => clearTimeout(timer)
  }, [value, delay])

  const changeColorClass = {
    positive: 'text-green-600 bg-green-50',
    negative: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-50'
  }[changeType]

  return (
    <Card className={cn(
      "hover-lift transition-all duration-300 border-0 shadow-lg bg-white/70 backdrop-blur-sm",
      isVisible ? "animate-fade-in" : "opacity-0"
    )}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900">
                {typeof value === 'number' ? displayValue.toLocaleString() : value}
              </p>
              {change && (
                <span className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                  changeColorClass
                )}>
                  {change}
                </span>
              )}
            </div>
            {description && (
              <p className="mt-1 text-sm text-gray-500">{description}</p>
            )}
          </div>
          
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
