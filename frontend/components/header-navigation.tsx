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
  X,
  Shield
} from 'lucide-react'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Activity
  },
  {
    name: 'Threat Monitoring',
    href: '/threat-monitoring',
    icon: Shield
  },
  {
    name: 'SQL Query',
    href: '/sql-query',
    icon: Terminal
  },
  {
    name: 'Database',
    href: '/database',
    icon: Database
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText
  },
  {
    name: 'Network Monitor',
    href: '/network-monitor',
    icon: Eye
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings
  }
]

export default function HeaderNavigation() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              {/* Logo */}
              <Image
                src="/Gemini_Generated_Image_ibutc6ibutc6ibut-removebg-preview.png"
                alt="CyberGuard Logo"
                width={40}
                height={40}
                className="w-10 h-10 object-contain"
              />
              <div>
                <h1 className="text-xl font-bold text-gray-900">CyberGuard</h1>
                <p className="text-xs text-gray-500">IDS/IPS Platform</p>
              </div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link key={item.name} href={item.href}>
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    size="sm"
                    className={`flex items-center space-x-2 ${
                      isActive 
                        ? 'bg-blue-600 text-white hover:bg-blue-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden lg:inline">{item.name}</span>
                  </Button>
                </Link>
              )
            })}
          </nav>

          {/* Status and Mobile Menu */}
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="hidden sm:flex text-green-600 border-green-600">
              <div className="w-2 h-2 bg-green-600 rounded-full mr-2 animate-pulse" />
              Online
            </Badge>
            
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isOpen && (
          <div className="md:hidden border-t border-gray-200 py-2">
            <div className="grid grid-cols-2 gap-2 px-2 py-2">
              {navigationItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                
                return (
                  <Link key={item.name} href={item.href} onClick={() => setIsOpen(false)}>
                    <div className={`flex items-center space-x-3 p-3 rounded-lg ${
                      isActive 
                        ? 'bg-blue-600 text-white' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}>
                      <Icon className="h-5 w-5" />
                      <span className="font-medium text-sm">{item.name}</span>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
