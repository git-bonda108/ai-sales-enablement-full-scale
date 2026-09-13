
"use client"

import Navigation from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { mockDashboardData } from '@/lib/mock-data'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Users, 
  Clock,
  DollarSign,
  Brain,
  Filter,
  Download,
  Calendar
} from 'lucide-react'

const advancedMetrics = [
  {
    title: 'Conversion Rate by Stage',
    data: [
      { stage: 'Prospect → Qualify', rate: 68, change: '+5%', trend: 'up' },
      { stage: 'Qualify → Proposal', rate: 45, change: '+8%', trend: 'up' },
      { stage: 'Proposal → Negotiation', rate: 72, change: '-2%', trend: 'down' },
      { stage: 'Negotiation → Close', rate: 89, change: '+12%', trend: 'up' }
    ]
  }
]

const revenueByIndustry = [
  { industry: 'Technology', revenue: 245000, deals: 8, avgDeal: 30625 },
  { industry: 'Financial Services', revenue: 198000, deals: 6, avgDeal: 33000 },
  { industry: 'Healthcare', revenue: 167000, deals: 4, avgDeal: 41750 },
  { industry: 'Manufacturing', revenue: 134000, deals: 3, avgDeal: 44667 },
  { industry: 'Retail', revenue: 103000, deals: 2, avgDeal: 51500 }
]

const aiPerformanceData = [
  { month: 'Sep', accuracy: 82.1, insights: 89, satisfaction: 4.1 },
  { month: 'Oct', accuracy: 84.5, insights: 112, satisfaction: 4.2 },
  { month: 'Nov', accuracy: 86.8, insights: 134, satisfaction: 4.3 },
  { month: 'Dec', accuracy: 87.9, insights: 142, satisfaction: 4.3 },
  { month: 'Jan', accuracy: 88.9, insights: 156, satisfaction: 4.4 }
]

const salesCycleData = [
  { stage: 'Prospecting', avgDays: 12, industry: 'avg' },
  { stage: 'Qualification', avgDays: 8, industry: 'avg' },
  { stage: 'Proposal', avgDays: 15, industry: 'avg' },
  { stage: 'Negotiation', avgDays: 10, industry: 'avg' }
]

const COLORS = ['#60B5FF', '#FF9149', '#FF9898', '#FF90BB', '#72BF78', '#A19AD3']

export default function AnalyticsPage() {
  const data = mockDashboardData

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navigation />
      
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  Advanced Analytics
                </h1>
                <p className="text-lg text-gray-600">
                  Deep insights into sales performance, AI effectiveness, and pipeline optimization
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" className="bg-white/70 backdrop-blur-sm border-0 shadow-lg">
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
                <Button variant="outline" className="bg-white/70 backdrop-blur-sm border-0 shadow-lg">
                  <Calendar className="h-4 w-4 mr-2" />
                  Date Range
                </Button>
                <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
              </div>
            </div>
          </div>

          {/* Key Performance Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Pipeline Velocity</p>
                    <p className="text-2xl font-bold text-gray-900">37 days</p>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingDown className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600 font-medium">-8 days</span>
                    </div>
                  </div>
                  <div className="h-12 w-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Lead Quality Score</p>
                    <p className="text-2xl font-bold text-gray-900">8.7/10</p>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600 font-medium">+0.5</span>
                    </div>
                  </div>
                  <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                    <Target className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">AI Accuracy</p>
                    <p className="text-2xl font-bold text-gray-900">88.9%</p>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600 font-medium">+2.1%</span>
                    </div>
                  </div>
                  <div className="h-12 w-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Revenue per Rep</p>
                    <p className="text-2xl font-bold text-gray-900">$84.7K</p>
                    <div className="flex items-center gap-1 mt-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600 font-medium">+15%</span>
                    </div>
                  </div>
                  <div className="h-12 w-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* AI Performance Trends */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  AI Performance Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={aiPerformanceData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                      <XAxis 
                        dataKey="month" 
                        tick={{ fontSize: 10 }}
                        tickLine={false}
                      />
                      <YAxis 
                        tick={{ fontSize: 10 }}
                        tickLine={false}
                        label={{ 
                          value: 'Accuracy %', 
                          angle: -90, 
                          position: 'insideLeft',
                          style: { textAnchor: 'middle', fontSize: 11 }
                        }}
                      />
                      <Tooltip 
                        content={({ active, payload, label }) => {
                          if (active && payload && payload.length) {
                            return (
                              <div className="rounded-lg border bg-white p-3 shadow-lg">
                                <p className="font-medium text-gray-900">{label} 2024</p>
                                <p className="text-sm text-purple-600">
                                  Accuracy: {payload[0].value}%
                                </p>
                                <p className="text-sm text-blue-600">
                                  Insights: {aiPerformanceData.find(d => d.month === label)?.insights}
                                </p>
                                <p className="text-sm text-green-600">
                                  Satisfaction: {aiPerformanceData.find(d => d.month === label)?.satisfaction}/5.0
                                </p>
                              </div>
                            )
                          }
                          return null
                        }}
                        wrapperStyle={{ fontSize: 11 }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="accuracy" 
                        stroke="#8b5cf6" 
                        fill="url(#colorAccuracy)"
                        strokeWidth={3}
                      />
                      <defs>
                        <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Revenue by Industry */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  Revenue by Industry
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revenueByIndustry} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                      <XAxis 
                        dataKey="industry" 
                        tick={{ fontSize: 10 }}
                        tickLine={false}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis 
                        tick={{ fontSize: 10 }}
                        tickLine={false}
                        tickFormatter={(value) => `$${(value / 1000)}K`}
                      />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'revenue' ? formatCurrency(value as number) : value, 
                          name === 'revenue' ? 'Revenue' : name
                        ]}
                        wrapperStyle={{ fontSize: 11 }}
                      />
                      <Bar 
                        dataKey="revenue" 
                        fill="#60B5FF"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sales Cycle Analysis */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-green-600" />
                  Sales Cycle Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {salesCycleData.map((stage, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900">{stage.stage}</div>
                        <div className="text-sm text-gray-500">Average duration</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900">{stage.avgDays} days</div>
                        <div className="text-xs text-green-600">-2 days vs last month</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Conversion Funnel */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-orange-600" />
                  Conversion Rates
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {advancedMetrics[0].data.map((conversion, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-900">{conversion.stage}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-gray-900">{conversion.rate}%</span>
                          <div className={`flex items-center gap-1 ${
                            conversion.trend === 'up' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {conversion.trend === 'up' ? (
                              <TrendingUp className="h-3 w-3" />
                            ) : (
                              <TrendingDown className="h-3 w-3" />
                            )}
                            <span className="text-xs font-medium">{conversion.change}</span>
                          </div>
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            conversion.trend === 'up' ? 'bg-green-500' : 'bg-orange-500'
                          }`}
                          style={{ width: `${conversion.rate}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Performers */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  Top Performers
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: 'Alex Johnson', deals: 8, revenue: 245000, winRate: 85 },
                    { name: 'Sarah Wilson', deals: 6, revenue: 198000, winRate: 78 },
                    { name: 'Mike Chen', deals: 5, revenue: 167000, winRate: 82 },
                    { name: 'Emma Davis', deals: 4, revenue: 134000, winRate: 75 }
                  ].map((rep, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`
                          w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold
                          ${index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-blue-500'}
                        `}>
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{rep.name}</div>
                          <div className="text-sm text-gray-500">{rep.deals} deals • {rep.winRate}% win rate</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-gray-900">{formatCurrency(rep.revenue)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
