
"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { mockDashboardData } from '@/lib/mock-data'
import { getInitials } from '@/lib/utils'
import { Phone, Mail, Lightbulb, RefreshCw } from 'lucide-react'

const activityIcons = {
  call: Phone,
  email: Mail,
  insight: Lightbulb,
  update: RefreshCw
}

const activityColors = {
  call: 'bg-blue-100 text-blue-600',
  email: 'bg-green-100 text-green-600',
  insight: 'bg-purple-100 text-purple-600',
  update: 'bg-orange-100 text-orange-600'
}

export default function RecentActivity() {
  return (
    <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover-lift">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-gray-900">
          Recent Activity
          <Badge variant="secondary" className="ml-2">
            {mockDashboardData.recentActivity.length} updates
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockDashboardData.recentActivity.map((activity, index) => {
            const Icon = activityIcons[activity.type as keyof typeof activityIcons]
            const colorClass = activityColors[activity.type as keyof typeof activityColors]
            
            return (
              <div key={index} className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${colorClass}`}>
                  <Icon className="h-5 w-5" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {activity.contact}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {activity.company}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-500">
                    {activity.type === 'call' && 'Sales call completed'}
                    {activity.type === 'email' && 'Email interaction logged'}
                    {activity.type === 'insight' && 'AI insight generated'}
                    {activity.type === 'update' && 'CRM record updated'}
                  </p>
                </div>
                
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{activity.value}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            )
          })}
        </div>
        
        <div className="mt-6 pt-4 border-t border-gray-200">
          <button className="w-full text-sm text-blue-600 hover:text-blue-700 font-medium">
            View all activity →
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
