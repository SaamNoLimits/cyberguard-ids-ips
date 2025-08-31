"use client"

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Database, 
  BarChart3, 
  Activity, 
  Settings, 
  Users, 
  FileText,
  Terminal,
  Eye,
  Menu,
  X
} from 'lucide-react'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Activity,
    description: 'Main overview'
  },
  {
    name: 'Threat Monitoring',
    href: '/threat-monitoring',
    icon: Shield,
    description: 'Real-time threats'
  },
  {
    name: 'SQL Query',
    href: '/sql-query',
    icon: Terminal,
    description: 'Custom queries'
  },
  {
    name: 'Database',
    href: '/database',
    icon: Database,
    description: 'Database explorer'
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    description: 'Data visualization'
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Security reports'
  },
  {
    name: 'Network Monitor',
    href: '/network-monitor',
    icon: Eye,
    description: 'Network activity'
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users,
    description: 'User management'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System config'
  }
]

export default function MainNavigation() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden lg:flex bg-gray-900 text-white p-4 space-x-1">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-blue-400" />
            <span className="text-xl font-bold">CyberGuard IDS/IPS</span>
          </div>
          
          <div className="flex space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link key={item.name} href={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    size="sm"
                    className={`flex items-center space-x-2 ${
                      isActive 
                        ? 'bg-blue-600 text-white hover:bg-blue-700' 
                        : 'text-gray-300 hover:text-white hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Button>
                </Link>
              )
            })}
          </div>
        </div>
        
        <div className="ml-auto flex items-center space-x-4">
          <Badge variant="outline" className="text-green-400 border-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
            System Online
          </Badge>
        </div>
      </nav>

      {/* Mobile Navigation */}
      <nav className="lg:hidden bg-gray-900 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-6 w-6 text-blue-400" />
            <span className="text-lg font-bold">CyberGuard</span>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className="text-white"
          >
            {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="mt-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link key={item.name} href={item.href} onClick={() => setIsOpen(false)}>
                  <div className={`flex items-center space-x-3 p-3 rounded-lg ${
                    isActive 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`}>
                    <Icon className="h-5 w-5" />
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-400">{item.description}</div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </nav>
    </>
  )
}
