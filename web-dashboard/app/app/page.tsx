
import Navigation from '@/components/navigation'
import MetricsCard from '@/components/metrics-card'
import PipelineChart from '@/components/pipeline-chart'
import RevenueChart from '@/components/revenue-chart'
import RecentActivity from '@/components/recent-activity'
import { mockDashboardData } from '@/lib/mock-data'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { Brain, Users, Target, BarChart3 } from 'lucide-react'

export default function Dashboard() {
  const data = mockDashboardData

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navigation />
      
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Sales Dashboard
            </h1>
            <p className="text-lg text-gray-600">
              Transform your sales process with AI-powered insights and automation
            </p>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricsCard
              title="Total Contacts"
              value={data.totalContacts}
              change="+12%"
              changeType="positive"
              iconName="Users"
              description="Active in pipeline"
              delay={0}
            />
            <MetricsCard
              title="Monthly Revenue"
              value={formatCurrency(data.monthlyRevenue)}
              change="+18%"
              changeType="positive"
              iconName="DollarSign"
              description="This month's performance"
              delay={100}
            />
            <MetricsCard
              title="Win Rate"
              value={formatPercentage(data.winRate)}
              change="+5%"
              changeType="positive"
              iconName="Target"
              description="Deals closed successfully"
              delay={200}
            />
            <MetricsCard
              title="Avg Sales Cycle"
              value={`${data.avgSalesCycle} days`}
              change="-8%"
              changeType="positive"
              iconName="Clock"
              description="Time to close deals"
              delay={300}
            />
          </div>

          {/* AI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricsCard
              title="AI Insights Generated"
              value={data.aiInsightsGenerated}
              change="+23 this week"
              changeType="positive"
              iconName="Brain"
              description="Automated analysis"
              delay={400}
            />
            <MetricsCard
              title="User Satisfaction"
              value={`${data.userSatisfactionScore}/5.0`}
              change="Excellent"
              changeType="positive"
              iconName="Star"
              description="AI accuracy rating"
              delay={500}
            />
            <MetricsCard
              title="Active Deals"
              value={data.activeDeals}
              change="+3 this week"
              changeType="positive"
              iconName="TrendingUp"
              description="In progress pipeline"
              delay={600}
            />
            <MetricsCard
              title="Avg Deal Size"
              value={formatCurrency(data.avgDealSize)}
              change="+15%"
              changeType="positive"
              iconName="BarChart3"
              description="Revenue per deal"
              delay={700}
            />
          </div>

          {/* Charts and Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <PipelineChart />
            <RevenueChart />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <RecentActivity />
            
            {/* Quick Actions Card */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg p-6 border-0 hover-lift">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-4">
                <button className="flex items-center gap-3 p-4 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors text-left">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <div>
                    <div className="font-medium text-blue-900">AI Chat</div>
                    <div className="text-sm text-blue-600">Get insights</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 rounded-lg bg-green-50 hover:bg-green-100 transition-colors text-left">
                  <Users className="h-5 w-5 text-green-600" />
                  <div>
                    <div className="font-medium text-green-900">CRM Sync</div>
                    <div className="text-sm text-green-600">Update records</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 rounded-lg bg-purple-50 hover:bg-purple-100 transition-colors text-left">
                  <BarChart3 className="h-5 w-5 text-purple-600" />
                  <div>
                    <div className="font-medium text-purple-900">Analytics</div>
                    <div className="text-sm text-purple-600">View reports</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 rounded-lg bg-orange-50 hover:bg-orange-100 transition-colors text-left">
                  <Target className="h-5 w-5 text-orange-600" />
                  <div>
                    <div className="font-medium text-orange-900">Training</div>
                    <div className="text-sm text-orange-600">Model status</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
