
"use client"

import { useState, useEffect } from 'react'
import Navigation from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { mockTrainingPipeline } from '@/lib/mock-data'
import { formatRelativeTime } from '@/lib/utils'
import { 
  Brain, 
  Database, 
  Cpu, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  TrendingUp,
  FileText,
  Mail,
  Users,
  Zap,
  Settings,
  PlayCircle,
  PauseCircle,
  RotateCcw
} from 'lucide-react'

export default function TrainingPage() {
  const [isTraining, setIsTraining] = useState(false)
  const [trainingProgress, setTrainingProgress] = useState(0)
  const data = mockTrainingPipeline

  useEffect(() => {
    if (isTraining) {
      const interval = setInterval(() => {
        setTrainingProgress(prev => {
          if (prev >= 100) {
            setIsTraining(false)
            return 0
          }
          return prev + 2
        })
      }, 100)
      return () => clearInterval(interval)
    }
  }, [isTraining])

  const startTraining = () => {
    setIsTraining(true)
    setTrainingProgress(0)
  }

  const processingStats = [
    { label: 'Queued', value: data.processingStatus.queued, color: 'text-yellow-600 bg-yellow-100' },
    { label: 'Processing', value: data.processingStatus.processing, color: 'text-blue-600 bg-blue-100' },
    { label: 'Completed', value: data.processingStatus.completed, color: 'text-green-600 bg-green-100' },
    { label: 'Failed', value: data.processingStatus.failed, color: 'text-red-600 bg-red-100' }
  ]

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navigation />
      
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Training Pipeline
            </h1>
            <p className="text-lg text-gray-600">
              Continuous learning and model improvement with real-time performance monitoring
            </p>
          </div>

          {/* Pipeline Overview */}
          <div className="mb-8">
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-purple-600" />
                  Training Pipeline Flow
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  {[
                    { icon: Database, label: 'Data Ingestion', status: 'completed', count: '1.2K files' },
                    { icon: Settings, label: 'Preprocessing', status: 'processing', count: '7 active' },
                    { icon: Brain, label: 'Model Training', status: isTraining ? 'processing' : 'ready', count: 'v2.3.1' },
                    { icon: CheckCircle, label: 'Validation', status: 'completed', count: '88.9%' },
                    { icon: TrendingUp, label: 'Deployment', status: 'completed', count: 'Live' }
                  ].map((step, index) => (
                    <div key={index} className="text-center">
                      <div className={`
                        w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center
                        ${step.status === 'completed' ? 'bg-green-100 text-green-600' :
                          step.status === 'processing' ? 'bg-blue-100 text-blue-600 animate-pulse' :
                          'bg-gray-100 text-gray-600'}
                      `}>
                        <step.icon className="h-8 w-8" />
                      </div>
                      <h3 className="font-medium text-gray-900 mb-1">{step.label}</h3>
                      <p className="text-sm text-gray-500">{step.count}</p>
                      {index < 4 && (
                        <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gray-300 transform translate-x-4"></div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Data Ingestion */}
            <div className="space-y-6">
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5 text-blue-600" />
                    Data Sources
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="font-medium text-blue-900">Call Transcripts</div>
                        <div className="text-sm text-blue-600">{data.dataIngested.totalTranscripts.toLocaleString()} files</div>
                      </div>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-green-600" />
                      <div>
                        <div className="font-medium text-green-900">Email Interactions</div>
                        <div className="text-sm text-green-600">{data.dataIngested.totalEmails.toLocaleString()} messages</div>
                      </div>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Users className="h-5 w-5 text-purple-600" />
                      <div>
                        <div className="font-medium text-purple-900">CRM Records</div>
                        <div className="text-sm text-purple-600">{data.dataIngested.totalCrmRecords.toLocaleString()} contacts</div>
                      </div>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  
                  <div className="pt-3 border-t border-gray-200">
                    <div className="text-sm text-gray-500">
                      Last updated: {formatRelativeTime(data.dataIngested.lastUpdated)}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Processing Status */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-orange-600" />
                    Processing Queue
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {processingStats.map((stat, index) => (
                      <div key={index} className="text-center p-3 rounded-lg bg-gray-50">
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${stat.color} mb-2`}>
                          {stat.label}
                        </div>
                        <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Model Performance */}
            <div className="space-y-6">
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    Model Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Current Version</div>
                    <div className="text-2xl font-bold text-gray-900 mb-2">{data.modelPerformance.currentVersion}</div>
                    <Badge className="bg-green-100 text-green-800">Production</Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{data.modelPerformance.accuracy}%</div>
                      <div className="text-sm text-green-700">Accuracy</div>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{data.modelPerformance.latency}s</div>
                      <div className="text-sm text-blue-700">Avg Latency</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Last Training</span>
                      <span className="font-medium">{formatRelativeTime(data.modelPerformance.lastTraining)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Next Training</span>
                      <span className="font-medium">{new Date(data.modelPerformance.nextTraining).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Training Controls */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5 text-gray-600" />
                    Training Controls
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {isTraining && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Cpu className="h-4 w-4 text-blue-600 animate-spin" />
                        <span className="text-sm font-medium text-blue-900">Training in Progress</span>
                      </div>
                      <Progress value={trainingProgress} className="h-2 mb-2" />
                      <div className="text-xs text-blue-600">{trainingProgress.toFixed(0)}% complete</div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 gap-3">
                    <Button 
                      onClick={startTraining}
                      disabled={isTraining}
                      className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700"
                    >
                      {isTraining ? (
                        <>
                          <PauseCircle className="h-4 w-4 mr-2" />
                          Training...
                        </>
                      ) : (
                        <>
                          <PlayCircle className="h-4 w-4 mr-2" />
                          Start Training
                        </>
                      )}
                    </Button>
                    
                    <Button variant="outline" className="bg-white/50">
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Rollback Version
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Feedback & Analytics */}
            <div className="space-y-6">
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    Feedback Analytics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center p-4 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-green-600 mb-1">{data.feedbackStats.positiveRating}%</div>
                    <div className="text-sm text-green-700">Positive Rating</div>
                    <div className="text-xs text-gray-500 mt-1">
                      From {data.feedbackStats.totalFeedback} user interactions
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-xl font-bold text-blue-600">{data.feedbackStats.improvements}</div>
                      <div className="text-xs text-blue-700">Improvements</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-xl font-bold text-orange-600">{data.feedbackStats.corrections}</div>
                      <div className="text-xs text-orange-700">Corrections</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* System Health */}
              <Card className="border-0 shadow-lg bg-green-50 border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <CheckCircle className="h-5 w-5" />
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-700">Model Status</span>
                      <Badge className="bg-green-100 text-green-800">Operational</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-700">API Uptime</span>
                      <span className="text-sm font-medium text-green-800">99.9%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-700">Response Time</span>
                      <span className="text-sm font-medium text-green-800">&lt; 800ms</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-700">Error Rate</span>
                      <span className="text-sm font-medium text-green-800">0.1%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-gray-600" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                      <span className="text-gray-700">Model v2.3.1 deployed successfully</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
                      <span className="text-gray-700">Processed 247 new transcripts</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-purple-500 rounded-full"></div>
                      <span className="text-gray-700">Feedback integration completed</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-orange-500 rounded-full"></div>
                      <span className="text-gray-700">Performance metrics updated</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
