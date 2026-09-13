
"use client"

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { mockDashboardData } from '@/lib/mock-data'
import { formatCurrency } from '@/lib/utils'

const stageColors = {
  prospecting: '#60B5FF',
  qualification: '#FF9149', 
  proposal: '#FF9898',
  negotiation: '#FF90BB',
  'closed-won': '#72BF78'
}

export default function PipelineChart() {
  const data = mockDashboardData.dealsByStage.map(stage => ({
    stage: stage.stage.charAt(0).toUpperCase() + stage.stage.slice(1).replace('-', ' '),
    count: stage.count,
    value: stage.value,
    fill: stageColors[stage.stage as keyof typeof stageColors]
  }))

  return (
    <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-gray-900">
          Pipeline by Stage
          <span className="text-sm font-normal text-gray-500">
            Current deals in progress
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <XAxis 
                dataKey="stage" 
                tick={{ fontSize: 10 }}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis 
                tick={{ fontSize: 10 }}
                tickLine={false}
                label={{ 
                  value: 'Deal Count', 
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
                        <p className="font-medium text-gray-900">{label}</p>
                        <p className="text-sm text-blue-600">
                          Deals: {payload[0].value}
                        </p>
                        <p className="text-sm text-green-600">
                          Value: {formatCurrency(data.find(d => d.stage === label)?.value || 0)}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
                wrapperStyle={{ fontSize: 11 }}
              />
              <Bar 
                dataKey="count" 
                radius={[4, 4, 0, 0]}
                className="hover:opacity-80 transition-opacity"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
