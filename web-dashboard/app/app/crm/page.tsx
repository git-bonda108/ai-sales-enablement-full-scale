
"use client"

import { useState } from 'react'
import Navigation from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Input } from '@/components/ui/input'
import { mockContacts } from '@/lib/mock-data'
import { formatCurrency, getInitials, formatRelativeTime } from '@/lib/utils'
import { 
  Users, 
  Search, 
  Filter, 
  Phone, 
  Mail, 
  Building2, 
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Star,
  Edit
} from 'lucide-react'

export default function CRMPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStage, setSelectedStage] = useState('all')
  const [selectedContact, setSelectedContact] = useState(mockContacts[0])

  const filteredContacts = mockContacts.filter(contact => {
    const matchesSearch = contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStage = selectedStage === 'all' || contact.dealStage === selectedStage
    return matchesSearch && matchesStage
  })

  const stageColors = {
    prospecting: 'bg-blue-100 text-blue-800',
    qualification: 'bg-yellow-100 text-yellow-800',
    proposal: 'bg-purple-100 text-purple-800',
    negotiation: 'bg-orange-100 text-orange-800',
    'closed-won': 'bg-green-100 text-green-800',
    'closed-lost': 'bg-red-100 text-red-800'
  }

  const priorityColors = {
    high: 'text-red-600',
    medium: 'text-yellow-600',
    low: 'text-green-600'
  }

  const stageIcons = {
    prospecting: Clock,
    qualification: Search,
    proposal: Edit,
    negotiation: TrendingUp,
    'closed-won': CheckCircle,
    'closed-lost': AlertCircle
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Navigation />
      
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              CRM Integration
            </h1>
            <p className="text-lg text-gray-600">
              Unified contact management with AI-powered insights and deal tracking
            </p>
          </div>

          {/* Filters and Search */}
          <div className="mb-6 flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search contacts, companies, or emails..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-0 shadow-lg bg-white/70 backdrop-blur-sm"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                className="px-4 py-2 rounded-md border-0 shadow-lg bg-white/70 backdrop-blur-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Stages</option>
                <option value="prospecting">Prospecting</option>
                <option value="qualification">Qualification</option>
                <option value="proposal">Proposal</option>
                <option value="negotiation">Negotiation</option>
                <option value="closed-won">Closed Won</option>
                <option value="closed-lost">Closed Lost</option>
              </select>
              <Button variant="outline" className="bg-white/70 backdrop-blur-sm border-0 shadow-lg">
                <Filter className="h-4 w-4 mr-2" />
                More Filters
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Contacts List */}
            <div>
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-600" />
                    Contacts ({filteredContacts.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="max-h-[600px] overflow-y-auto">
                    {filteredContacts.map((contact) => {
                      const StageIcon = stageIcons[contact.dealStage]
                      const isSelected = selectedContact.id === contact.id
                      
                      return (
                        <div
                          key={contact.id}
                          onClick={() => setSelectedContact(contact)}
                          className={`
                            p-4 border-b border-gray-100 cursor-pointer transition-all duration-200 hover:bg-gray-50
                            ${isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''}
                          `}
                        >
                          <div className="flex items-center gap-4">
                            <Avatar className="h-12 w-12">
                              <AvatarImage src={contact.avatar} alt={contact.name} />
                              <AvatarFallback className="bg-gray-200">
                                {getInitials(contact.name)}
                              </AvatarFallback>
                            </Avatar>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900 truncate">
                                  {contact.name}
                                </h3>
                                <Star className={`h-4 w-4 ${priorityColors[contact.priority]}`} />
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                                <Building2 className="h-3 w-3" />
                                <span className="truncate">{contact.company}</span>
                                <span>•</span>
                                <span>{contact.role}</span>
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <Badge className={stageColors[contact.dealStage]}>
                                  <StageIcon className="h-3 w-3 mr-1" />
                                  {contact.dealStage.replace('-', ' ')}
                                </Badge>
                                <span className="text-sm font-medium text-gray-900">
                                  {formatCurrency(contact.dealValue)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Contact Details */}
            <div className="space-y-6">
              {/* Contact Info */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={selectedContact.avatar} alt={selectedContact.name} />
                        <AvatarFallback className="bg-gray-200">
                          {getInitials(selectedContact.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">{selectedContact.name}</h2>
                        <p className="text-gray-600">{selectedContact.role}</p>
                      </div>
                    </div>
                    <Button size="sm" className="bg-gradient-to-r from-blue-500 to-purple-600">
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="outline" className="justify-start bg-white/50">
                      <Phone className="h-4 w-4 mr-2" />
                      {selectedContact.phone}
                    </Button>
                    <Button variant="outline" className="justify-start bg-white/50">
                      <Mail className="h-4 w-4 mr-2" />
                      Email
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Company</span>
                      <span className="text-sm font-medium">{selectedContact.company}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Industry</span>
                      <span className="text-sm font-medium">{selectedContact.industry}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Deal Value</span>
                      <span className="text-sm font-medium text-green-600">
                        {formatCurrency(selectedContact.dealValue)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Priority</span>
                      <Badge variant="outline" className={priorityColors[selectedContact.priority]}>
                        {selectedContact.priority}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Last Contact</span>
                      <span className="text-sm font-medium">
                        {formatRelativeTime(selectedContact.lastInteraction)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Deal Status */}
              <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    Deal Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Current Stage</span>
                      <Badge className={stageColors[selectedContact.dealStage]}>
                        {selectedContact.dealStage.replace('-', ' ')}
                      </Badge>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Prospecting</span>
                        <span>Closed</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                          style={{ 
                            width: `${
                              selectedContact.dealStage === 'prospecting' ? '20%' :
                              selectedContact.dealStage === 'qualification' ? '40%' :
                              selectedContact.dealStage === 'proposal' ? '60%' :
                              selectedContact.dealStage === 'negotiation' ? '80%' :
                              '100%'
                            }` 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Insights */}
              <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-purple-600" />
                    AI Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-white/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Calendar className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium">Next Action</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Schedule technical demo with IT security team by Tuesday
                      </p>
                    </div>
                    
                    <div className="p-3 bg-white/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium">Win Probability</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold text-green-600">85%</span> based on engagement and security focus
                      </p>
                    </div>
                    
                    <div className="p-3 bg-white/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <AlertCircle className="h-4 w-4 text-orange-600" />
                        <span className="text-sm font-medium">Key Concern</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Data privacy and compliance requirements need addressing
                      </p>
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
