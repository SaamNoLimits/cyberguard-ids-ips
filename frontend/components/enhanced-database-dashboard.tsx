"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Database, Download, Search, Filter, RefreshCw, BarChart3, Eye } from 'lucide-react'

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

export default function EnhancedDatabaseDashboard() {
  const [threats, setThreats] = useState<ThreatRecord[]>([])
  const [filteredThreats, setFilteredThreats] = useState<ThreatRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [attackTypeFilter, setAttackTypeFilter] = useState('all')
  const [threatLevelFilter, setThreatLevelFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(0)
  const [limit] = useState(100)
  const [stats, setStats] = useState<any>(null)

  const fetchAllData = async () => {
    try {
      setLoading(true)
      
      // Fetch database stats
      const statsResponse = await fetch('http://localhost:8000/api/database/stats')
      const statsData = await statsResponse.json()
      setStats(statsData)

      // Fetch all threats (large dataset)
      const threatsResponse = await fetch(`http://localhost:8000/api/database/threats/recent?limit=1000`)
      const threatsData = await threatsResponse.json()
      setThreats(threatsData.threats || [])
      setFilteredThreats(threatsData.threats || [])
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter and search logic
  useEffect(() => {
    let filtered = threats

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(threat => 
        threat.source_ip.includes(searchTerm) ||
        threat.destination_ip.includes(searchTerm) ||
        threat.attack_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        threat.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Attack type filter
    if (attackTypeFilter !== 'all') {
      filtered = filtered.filter(threat => threat.attack_type === attackTypeFilter)
    }

    // Threat level filter
    if (threatLevelFilter !== 'all') {
      filtered = filtered.filter(threat => threat.threat_level === threatLevelFilter)
    }

    setFilteredThreats(filtered)
    setCurrentPage(0)
  }, [searchTerm, attackTypeFilter, threatLevelFilter, threats])

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
        alert('PCAP file not available')
      }
    } catch (error) {
      console.error('Error downloading PCAP:', error)
    }
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

  const uniqueAttackTypes = [...new Set(threats.map(t => t.attack_type))]
  const uniqueThreatLevels = [...new Set(threats.map(t => t.threat_level))]

  const paginatedThreats = filteredThreats.slice(currentPage * limit, (currentPage + 1) * limit)

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading && threats.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Database className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Loading database...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Database Dashboard</h1>
          <p className="text-muted-foreground">Complete database view with filtering and analysis</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchAllData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
          <Badge variant="outline">
            <Database className="h-4 w-4 mr-1" />
            {stats?.total_threats?.toLocaleString() || 0} Total
          </Badge>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Threats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_threats?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Filtered Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredThreats.length.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">PCAP Files</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pcap_files_count || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Attack Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uniqueAttackTypes.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search IPs, attack types..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={attackTypeFilter} onValueChange={setAttackTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Attack Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Attack Types</SelectItem>
                {uniqueAttackTypes.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={threatLevelFilter} onValueChange={setThreatLevelFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Threat Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                {uniqueThreatLevels.map(level => (
                  <SelectItem key={level} value={level}>{level}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              onClick={() => {
                setSearchTerm('')
                setAttackTypeFilter('all')
                setThreatLevelFilter('all')
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Threats Table */}
      <Card>
        <CardHeader>
          <CardTitle>Database Records ({filteredThreats.length.toLocaleString()} threats)</CardTitle>
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
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedThreats.map((threat) => (
                  <TableRow key={threat.id}>
                    <TableCell className="font-mono text-xs">
                      {formatTimestamp(threat.timestamp)}
                    </TableCell>
                    <TableCell className="font-mono">{threat.source_ip}</TableCell>
                    <TableCell className="font-mono">{threat.destination_ip}</TableCell>
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
                      <div className="flex gap-1">
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        {threat.pcap_file_path && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadPcap(threat.id, threat.attack_type)}
                          >
                            <Download className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-muted-foreground">
              Showing {currentPage * limit + 1}-{Math.min((currentPage + 1) * limit, filteredThreats.length)} of {filteredThreats.length.toLocaleString()} threats
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
                disabled={(currentPage + 1) * limit >= filteredThreats.length}
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
