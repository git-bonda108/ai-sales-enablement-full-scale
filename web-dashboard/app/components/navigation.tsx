
"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  Users, 
  Brain, 
  BarChart3,
  Zap,
  Settings
} from 'lucide-react'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    description: 'Overview and key metrics'
  },
  {
    name: 'AI Assistant',
    href: '/chat',
    icon: MessageSquare,
    description: 'Chat with your sales AI'
  },
  {
    name: 'Transcripts',
    href: '/transcripts',
    icon: FileText,
    description: 'Call analysis and insights'
  },
  {
    name: 'CRM Integration',
    href: '/crm',
    icon: Users,
    description: 'Contact and deal management'
  },
  {
    name: 'Training Pipeline',
    href: '/training',
    icon: Brain,
    description: 'Model training and performance'
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    description: 'Advanced sales analytics'
  }
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-64 flex-col bg-white/80 backdrop-blur-xl border-r border-gray-200/50 shadow-xl">
      {/* Logo and Header */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-gray-200/50">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
          <Zap className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">AI Sales Platform</h1>
          <p className="text-sm text-gray-500">v2.3.1</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-2 px-4 py-6">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-all duration-200 hover:bg-blue-50 hover:text-blue-700",
                isActive 
                  ? "bg-blue-100 text-blue-700 shadow-sm border-l-4 border-blue-500" 
                  : "text-gray-600 hover:translate-x-1"
              )}
            >
              <Icon className={cn(
                "h-5 w-5 transition-colors",
                isActive ? "text-blue-600" : "text-gray-400 group-hover:text-blue-500"
              )} />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs text-gray-500 group-hover:text-gray-600">
                  {item.description}
                </div>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Status Indicator */}
      <div className="border-t border-gray-200/50 px-4 py-4">
        <div className="flex items-center gap-3 rounded-lg bg-green-50 px-3 py-2">
          <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
          <div className="flex-1">
            <div className="text-sm font-medium text-green-800">System Operational</div>
            <div className="text-xs text-green-600">All services running</div>
          </div>
        </div>
      </div>
    </div>
  )
}
