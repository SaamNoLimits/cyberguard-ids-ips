"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Network, 
  Eye,
  Server,
  Zap,
  TrendingUp,
  Users,
  Lock,
  RefreshCw
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { apiClient, WebSocketClient } from '@/lib/api'

interface DashboardStats {
  total_devices: number
  active_threats: number
  blocked_attacks: number
  network_traffic: number
  threat_level: string
  uptime_hours: number
  last_updated: string
}

interface ThreatAlert {
  id: string
  timestamp: string
  source_ip: string
  destination_ip: string
  attack_type: string
  threat_level: string
  confidence: number
  description: string
  blocked: boolean
}

const THREAT_LEVEL_COLORS = {
  LOW: 'bg-green-500',
  MEDIUM: 'bg-yellow-500',
  HIGH: 'bg-orange-500',
  CRITICAL: 'bg-red-500'
}

const ATTACK_TYPE_COLORS = {
  'Flood Attacks': '#ef4444',
  'Botnet/Mirai Attacks': '#f97316',
  'Backdoors & Exploits': '#dc2626',
  'Injection Attacks': '#ea580c',
  'Reconnaissance': '#facc15',
  'Spoofing / MITM': '#a855f7',
  'Benign': '#22c55e'
}

export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats>({
    total_devices: 0,
    active_threats: 0,
    blocked_attacks: 0,
    network_traffic: 0,
    threat_level: 'LOW',
    uptime_hours: 0,
    last_updated: new Date().toISOString()
  })
  const [threats, setThreats] = useState<ThreatAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [isConnected, setIsConnected] = useState(false)
  const [wsClient] = useState(() => new WebSocketClient())
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting')
  const [trafficData, setTrafficData] = useState<any[]>([])
  const [attackData, setAttackData] = useState<any[]>([])

  useEffect(() => {
    loadDashboardData()

    // Auto-refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      loadDashboardData()
    }, 30000)

    wsClient.on('connected', () => setConnectionStatus('connected'))
    wsClient.on('disconnected', () => setConnectionStatus('disconnected'))
    wsClient.on('stats_update', (data: any) => {
      if (data.network_stats) {
        setStats(prev => prev ? { ...prev, ...data.network_stats } : null)
      }
      if (data.recent_alerts) {
        setThreats(data.recent_alerts)
      }
    })
    wsClient.connect()

    return () => {
      clearInterval(refreshInterval)
      wsClient.disconnect()
    }
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      setLastUpdate(new Date().toLocaleTimeString())
      
      // Fetch real dashboard statistics from backend
      const [statsResponse, threatsResponse, analyticsResponse] = await Promise.all([
        fetch('http://localhost:8000/api/dashboard/stats'),
        fetch('http://localhost:8000/api/threats/recent?limit=20'),
        fetch('http://localhost:8000/api/dashboard/analytics')
      ])
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats({
          total_devices: statsData.total_devices || 0,
          active_threats: statsData.active_threats || 0,
          blocked_attacks: statsData.blocked_attacks || 0,
          network_traffic: statsData.network_traffic || 0,
          threat_level: statsData.threat_level || 'LOW',
          uptime_hours: statsData.uptime_hours || 0,
          last_updated: new Date().toISOString()
        })
        setIsConnected(true)
      }
      
      if (threatsResponse.ok) {
        const threatsData = await threatsResponse.json()
        setThreats(threatsData.threats || [])
      }
      
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json()
        
        // Set real analytics data from database
        setAttackData(analyticsData.timeline || [])
        
        // Generate traffic data from analytics
        generateAnalyticsFromThreats(threats)
      }
      
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      setIsConnected(false)
      
      // Fallback to sample data if backend is unavailable
      loadSampleData()
    } finally {
      setIsLoading(false)
    }
  }
  
  const generateAnalyticsFromThreats = (threatData: ThreatAlert[]) => {
    // Generate hourly traffic data from threats
    const hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date()
      hour.setHours(hour.getHours() - (23 - i))
      const hourThreats = threatData.filter(threat => {
        const threatHour = new Date(threat.timestamp).getHours()
        return threatHour === hour.getHours()
      })
      
      return {
        time: hour.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        threats: hourThreats.length,
        blocked: hourThreats.filter((t: ThreatAlert) => t.blocked).length,
        traffic: Math.floor(Math.random() * 1000) + 500 // Simulated traffic volume
      }
    })
    
    setTrafficData(hourlyData)
    
    // Generate attack type distribution
    const attackTypes = threatData.reduce((acc: any, threat) => {
      acc[threat.attack_type] = (acc[threat.attack_type] || 0) + 1
      return acc
    }, {})
    
    const attackChartData = Object.entries(attackTypes).map(([type, count]) => ({
      name: type,
      value: count,
      blocked: threatData.filter(t => t.attack_type === type && t.blocked).length
    }))
    
    setAttackData(attackChartData)
  }
  
  const loadSampleData = () => {
    // Fallback sample data when backend is unavailable
    setStats({
      total_devices: 156,
      active_threats: 23,
      blocked_attacks: 1847,
      network_traffic: 2.4,
      threat_level: 'MEDIUM',
      uptime_hours: 720,
      last_updated: new Date().toISOString()
    })
    
    // Sample threat data
    const sampleThreats: ThreatAlert[] = [
      {
        id: '1',
        timestamp: new Date().toISOString(),
        source_ip: '192.168.1.100',
        destination_ip: '10.0.0.1',
        attack_type: 'Port Scan',
        threat_level: 'MEDIUM',
        confidence: 0.85,
        description: 'Suspicious port scanning activity detected',
        blocked: true
      }
    ]
    
    setThreats(sampleThreats)
    generateAnalyticsFromThreats(sampleThreats)
  }

  const getThreatLevelBadge = (level: string) => {
    const colorClass = THREAT_LEVEL_COLORS[level as keyof typeof THREAT_LEVEL_COLORS] || 'bg-gray-500'
    return <Badge className={`${colorClass} text-white`}>{level}</Badge>
  }

  const formatTimestamp = (timestamp: string) => new Date(timestamp).toLocaleString()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">IDS/IPS Dashboard</h1>
          <p className="text-muted-foreground">Real-time intrusion detection and prevention monitoring</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 
            connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
          }`} />
          <span className="text-sm text-muted-foreground">
            {connectionStatus === 'connected' ? 'Live' : 
             connectionStatus === 'connecting' ? 'Connecting' : 'Offline'}
          </span>
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network Devices</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_devices || 0}</div>
            <p className="text-xs text-muted-foreground">Active on network</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{stats?.active_threats || 0}</div>
            <p className="text-xs text-muted-foreground">Detected in last hour</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Attacks</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{stats?.blocked_attacks || 0}</div>
            <p className="text-xs text-muted-foreground">Automatically blocked</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network Traffic</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(stats?.network_traffic || 0).toFixed(1)} Mbps</div>
            <p className="text-xs text-muted-foreground">Current throughput</p>
          </CardContent>
        </Card>
      </div>

      {stats?.threat_level && stats.threat_level !== 'LOW' && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Elevated Threat Level</AlertTitle>
          <AlertDescription>
            Current threat level: {getThreatLevelBadge(stats.threat_level)}
            Enhanced monitoring is active.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Network Traffic (24h)</CardTitle>
                <CardDescription>Bytes in/out over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trafficData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                    <YAxis />
                    <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} formatter={(value: number) => [`${(value / 1024 / 1024).toFixed(2)} MB`, '']} />
                    <Line type="monotone" dataKey="bytes_in" stroke="#3b82f6" name="Bytes In" />
                    <Line type="monotone" dataKey="bytes_out" stroke="#ef4444" name="Bytes Out" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Attack Types (24h)</CardTitle>
                <CardDescription>Distribution of detected attacks</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={attackData.map(item => ({
                        name: item.attack_type,
                        value: item.count,
                        fill: ATTACK_TYPE_COLORS[item.attack_type as keyof typeof ATTACK_TYPE_COLORS] || '#6b7280'
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="threats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Threat Alerts</CardTitle>
              <CardDescription>Latest security incidents detected by the IDS</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {threats.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Shield className="h-12 w-12 mx-auto mb-4 text-green-500" />
                    <p>No threats detected. Your network is secure!</p>
                  </div>
                ) : (
                  threats.map((threat) => (
                    <div key={threat.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getThreatLevelBadge(threat.threat_level)}
                          <Badge variant={threat.blocked ? "default" : "destructive"}>
                            {threat.blocked ? "Blocked" : "Detected"}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {formatTimestamp(threat.timestamp)}
                          </span>
                        </div>
                        <h4 className="font-medium">{threat.attack_type}</h4>
                        <p className="text-sm text-muted-foreground">{threat.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                          <span>From: {threat.source_ip}</span>
                          <span>To: {threat.destination_ip}</span>
                          <span>Confidence: {(threat.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <Progress value={threat.confidence * 100} className="w-20" />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Attack Timeline</CardTitle>
                <CardDescription>Attack frequency over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={attackData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                    <YAxis />
                    <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
                    <Bar dataKey="count" fill="#ef4444" name="Total Attacks" />
                    <Bar dataKey="blocked_count" fill="#22c55e" name="Blocked" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Protocol Analysis</CardTitle>
                <CardDescription>Network traffic by protocol</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={trafficData.length > 0 ? Object.entries(trafficData[trafficData.length - 1]?.protocols || {}).map(([protocol, count]) => ({
                        name: protocol,
                        value: count,
                        fill: protocol === 'TCP' ? '#3b82f6' : protocol === 'UDP' ? '#ef4444' : '#22c55e'
                      })) : []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
