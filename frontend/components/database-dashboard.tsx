"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Database, Download, HardDrive, Clock, Shield, Search, Filter, Eye, Trash2, RefreshCw, BarChart3, PieChart, TrendingUp } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Cell, BarChart, Bar } from 'recharts'

interface DatabaseStats {
  total_threats: number
  recent_threats_24h: number
  threat_levels: Record<string, number>
  attack_types: Record<string, number>
  pcap_files_count: number
  total_storage_bytes: number
  storage_path: string
}

interface ThreatRecord {
  id: string
  timestamp: string
  source_ip: string
  destination_ip: string
  attack_type: string
  threat_level: string
  confidence: number
  description: string
  blocked: boolean
  pcap_file_path: string | null
  packet_count: number
  bytes_transferred: number
}

export default function DatabaseDashboard() {
  const [stats, setStats] = useState<DatabaseStats | null>(null)
  const [threats, setThreats] = useState<ThreatRecord[]>([])
  const [allThreats, setAllThreats] = useState<ThreatRecord[]>([])
  const [filteredThreats, setFilteredThreats] = useState<ThreatRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [limit] = useState(50)
  
  // Filter and search states
  const [searchTerm, setSearchTerm] = useState('')
  const [attackTypeFilter, setAttackTypeFilter] = useState('all')
  const [threatLevelFilter, setThreatLevelFilter] = useState('all')
  const [dateFilter, setDateFilter] = useState('all')
  const [sortBy, setSortBy] = useState('timestamp')
  const [sortOrder, setSortOrder] = useState('desc')
  
  // Chart data
  const [chartData, setChartData] = useState<any[]>([])
  const [pieChartData, setPieChartData] = useState<any[]>([])

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/database/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching database stats:', error)
    }
  }

  const fetchThreats = async (offset = 0) => {
    try {
      const response = await fetch(`http://localhost:8000/api/database/threats/recent?limit=${limit}&offset=${offset}`)
      const data = await response.json()
      setThreats(data.threats || [])
    } catch (error) {
      console.error('Error fetching threats:', error)
    }
  }

  const downloadPcap = async (threatId: string, attackType: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/pcap/download/${threatId}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `threat_${threatId}_${attackType}.pcap`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        alert('PCAP file not available for this threat')
      }
    } catch (error) {
      console.error('Error downloading PCAP:', error)
      alert('Error downloading PCAP file')
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-500'
      case 'HIGH': return 'bg-orange-500'
      case 'MEDIUM': return 'bg-yellow-500'
      case 'LOW': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([fetchDatabaseStats(), fetchThreats(currentPage * limit)])
      setLoading(false)
    }
    loadData()

    // Refresh data every 10 seconds
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [currentPage, limit])

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Database className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Loading database data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Database Dashboard</h1>
          <p className="text-muted-foreground">View all stored threats and database statistics</p>
        </div>
        <Badge variant="outline" className="text-sm">
          <Database className="h-4 w-4 mr-1" />
          PostgreSQL
        </Badge>
      </div>

      {/* Database Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_threats?.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.recent_threats_24h || 0} in last 24h
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PCAP Files</CardTitle>
            <HardDrive className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pcap_files_count || 0}</div>
            <p className="text-xs text-muted-foreground">
              {formatBytes(stats?.total_storage_bytes || 0)} used
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Attack Types</CardTitle>
            <Shield className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(stats?.attack_types || {}).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Different attack patterns
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Path</CardTitle>
            <Database className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-sm font-mono truncate">
              {stats?.storage_path?.split('/').slice(-2).join('/') || 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              PCAP storage location
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="threats" className="space-y-4">
        <TabsList>
          <TabsTrigger value="threats">Threat Records</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="threats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Database Threat Records</CardTitle>
              <CardDescription>
                All threats stored in PostgreSQL database with forensic data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Source IP</TableHead>
                      <TableHead>Destination IP</TableHead>
                      <TableHead>Attack Type</TableHead>
                      <TableHead>Level</TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>Packets</TableHead>
                      <TableHead>Bytes</TableHead>
                      <TableHead>PCAP</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {threats.map((threat) => (
                      <TableRow key={threat.id}>
                        <TableCell className="font-mono text-xs">
                          {formatTimestamp(threat.timestamp)}
                        </TableCell>
                        <TableCell className="font-mono">
                          {threat.source_ip}
                        </TableCell>
                        <TableCell className="font-mono">
                          {threat.destination_ip}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{threat.attack_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getThreatLevelColor(threat.threat_level)}>
                            {threat.threat_level}
                          </Badge>
                        </TableCell>
                        <TableCell>{(threat.confidence * 100).toFixed(1)}%</TableCell>
                        <TableCell>{threat.packet_count}</TableCell>
                        <TableCell>{threat.bytes_transferred}</TableCell>
                        <TableCell>
                          {threat.pcap_file_path ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => downloadPcap(threat.id, threat.attack_type)}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              Download
                            </Button>
                          ) : (
                            <span className="text-muted-foreground text-xs">N/A</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-muted-foreground">
                  Showing {threats.length} threats (Page {currentPage + 1})
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                    disabled={currentPage === 0}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(currentPage + 1)}
                    disabled={threats.length < limit}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Threat Levels Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(stats?.threat_levels || {}).map(([level, count]) => (
                    <div key={level} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge className={getThreatLevelColor(level)}>{level}</Badge>
                      </div>
                      <span className="font-mono">{count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Attack Types Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(stats?.attack_types || {}).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <Badge variant="outline">{type}</Badge>
                      <span className="font-mono">{count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
