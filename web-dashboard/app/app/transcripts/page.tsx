
"use client"

import { useState } from 'react'
import Navigation from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { mockTranscripts } from '@/lib/mock-data'
import { 
  FileText, 
  Upload, 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Users,
  MessageSquare,
  Target,
  Lightbulb
} from 'lucide-react'

export default function TranscriptsPage() {
  const [dragActive, setDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    // Simulate file upload and processing
    setIsProcessing(true)
    setUploadProgress(0)
    
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsProcessing(false)
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  const transcript = mockTranscripts[0]
  const insights = transcript.aiInsights

  const sentimentColor = {
    positive: 'text-green-600 bg-green-100',
    neutral: 'text-yellow-600 bg-yellow-100', 
    negative: 'text-red-600 bg-red-100'
  }[insights.sentiment]

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navigation />
      
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Transcript Analyzer
            </h1>
            <p className="text-lg text-gray-600">
              AI-powered analysis of sales calls with insights and coaching recommendations
            </p>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5 text-blue-600" />
                  Upload New Transcript
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className={`
                    border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
                    ${dragActive 
                      ? 'border-blue-400 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                    }
                  `}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {isProcessing ? (
                    <div className="space-y-4">
                      <Brain className="h-12 w-12 text-blue-500 mx-auto animate-pulse" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">Processing transcript...</p>
                        <p className="text-sm text-gray-500">AI is analyzing the conversation</p>
                      </div>
                      <div className="max-w-xs mx-auto">
                        <Progress value={uploadProgress} className="h-2" />
                        <p className="text-xs text-gray-500 mt-1">{uploadProgress}% complete</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          Drop transcript files here
                        </p>
                        <p className="text-sm text-gray-500">
                          Supports .txt, .docx, audio files, or paste transcript text
                        </p>
                      </div>
                      <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                        Browse Files
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Analysis Results */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Transcript */}
            <div className="lg:col-span-2 space-y-6">
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                    Call Transcript - Sarah Chen
                    <Badge className={sentimentColor}>
                      {insights.sentiment} sentiment
                    </Badge>
                  </CardTitle>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {transcript.duration} minutes
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      {transcript.participants.length} participants
                    </span>
                    <span>{new Date(transcript.date).toLocaleDateString()}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="max-h-96 overflow-y-auto space-y-4 p-4 bg-gray-50 rounded-lg">
                    {transcript.transcript.split('\n\n').map((paragraph, index) => (
                      <div key={index} className="text-sm leading-relaxed">
                        {paragraph.split(': ').length > 1 ? (
                          <div>
                            <span className="font-semibold text-blue-600">
                              {paragraph.split(': ')[0]}:
                            </span>
                            <span className="ml-2 text-gray-700">
                              {paragraph.split(': ').slice(1).join(': ')}
                            </span>
                          </div>
                        ) : (
                          <p className="text-gray-700">{paragraph}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Key Topics */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-purple-600" />
                    Key Topics Discussed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {insights.keyTopics.map((topic, index) => (
                      <Badge key={index} variant="outline" className="bg-purple-50 text-purple-700">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* AI Insights Sidebar */}
            <div className="space-y-6">
              {/* Next Steps */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    Next Steps
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {insights.nextSteps.map((step, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-green-500 mt-2 shrink-0"></div>
                        <span className="text-gray-700">{step}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Opportunities */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-600" />
                    Opportunities
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {insights.opportunities.map((opportunity, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-blue-500 mt-2 shrink-0"></div>
                        <span className="text-gray-700">{opportunity}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Concerns */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    Concerns Raised
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {insights.concerns.map((concern, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-orange-500 mt-2 shrink-0"></div>
                        <span className="text-gray-700">{concern}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Coaching Tips */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-yellow-600" />
                    Coaching Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {insights.coachingTips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <div className="h-2 w-2 rounded-full bg-yellow-500 mt-2 shrink-0"></div>
                        <span className="text-gray-700">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Deal Impact */}
              <Card className="border-0 shadow-lg bg-green-50 border-green-200">
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-800">Deal Impact</div>
                    <div className="text-sm text-green-600 mt-1">{transcript.dealImpact}</div>
                    <div className="text-xs text-green-500 mt-2">Outcome: {transcript.outcome}</div>
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
