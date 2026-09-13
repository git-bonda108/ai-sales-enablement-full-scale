
"use client"

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { mockDashboardData } from '@/lib/mock-data'
import { formatCurrency } from '@/lib/utils'

export default function RevenueChart() {
  const data = mockDashboardData.monthlyMetrics

  return (
    <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-gray-900">
          Revenue Trend
          <span className="text-sm font-normal text-gray-500">
            Monthly performance over time
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <XAxis 
                dataKey="month" 
                tick={{ fontSize: 10 }}
                tickLine={false}
                label={{ 
                  value: 'Month', 
                  position: 'insideBottom',
                  offset: -15,
                  style: { textAnchor: 'middle', fontSize: 11 }
                }}
              />
              <YAxis 
                tick={{ fontSize: 10 }}
                tickLine={false}
                label={{ 
                  value: 'Revenue ($)', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { textAnchor: 'middle', fontSize: 11 }
                }}
                tickFormatter={(value) => `$${(value / 1000)}K`}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 10 }}
                tickLine={false}
                label={{ 
                  value: 'Deals', 
                  angle: 90, 
                  position: 'insideRight',
                  style: { textAnchor: 'middle', fontSize: 11 }
                }}
              />
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="rounded-lg border bg-white p-3 shadow-lg">
                        <p className="font-medium text-gray-900">{label} 2024</p>
                        <p className="text-sm text-blue-600">
                          Revenue: {formatCurrency(payload[0].value as number)}
                        </p>
                        <p className="text-sm text-green-600">
                          Deals: {payload[1].value}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
                wrapperStyle={{ fontSize: 11 }}
              />
              <Legend 
                verticalAlign="top"
                wrapperStyle={{ fontSize: 11 }}
              />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke="#60B5FF" 
                strokeWidth={3}
                dot={{ r: 5, fill: '#60B5FF' }}
                name="Revenue"
                className="drop-shadow-sm"
              />
              <Line 
                type="monotone" 
                dataKey="deals" 
                stroke="#72BF78" 
                strokeWidth={3}
                dot={{ r: 5, fill: '#72BF78' }}
                name="Deals Closed"
                yAxisId="right"
                className="drop-shadow-sm"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
