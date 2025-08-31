"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Database, Download, Search, RefreshCw, Eye, Filter } from 'lucide-react'

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

interface DatabaseStats {
  total_threats: number
  recent_threats_24h: number
  threat_levels: Record<string, number>
  attack_types: Record<string, number>
  pcap_files_count: number
  total_storage_bytes: number
  storage_path: string
}

export default function SimpleDatabaseDashboard() {
  const [mounted, setMounted] = useState(false)
  const [threats, setThreats] = useState<ThreatRecord[]>([])
  const [filteredThreats, setFilteredThreats] = useState<ThreatRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [attackTypeFilter, setAttackTypeFilter] = useState('all')
  const [threatLevelFilter, setThreatLevelFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(0)
  const [limit] = useState(50)
  const [stats, setStats] = useState<DatabaseStats | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      
      // Fetch database stats
      const statsResponse = await fetch('http://localhost:8000/api/database/stats')
      const statsData = await statsResponse.json()
      setStats(statsData)

      // Fetch threats
      const threatsResponse = await fetch(`http://localhost:8000/api/database/threats/recent?limit=500`)
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
    if (!mounted) return timestamp
    return new Date(timestamp).toLocaleString()
  }

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-500 text-white'
      case 'HIGH': return 'bg-orange-500 text-white'
      case 'MEDIUM': return 'bg-yellow-500 text-black'
      case 'LOW': return 'bg-green-500 text-white'
      default: return 'bg-gray-500 text-white'
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

  if (!mounted) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading Database Dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading && threats.length === 0) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Database className="h-8 w-8 animate-spin mx-auto mb-2" />
            <p className="text-muted-foreground">Loading database...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
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
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Filtered Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredThreats.length.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Current view</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">PCAP Files</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pcap_files_count || 0}</div>
            <p className="text-xs text-muted-foreground">Available for download</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Attack Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uniqueAttackTypes.length}</div>
            <p className="text-xs text-muted-foreground">Different types detected</p>
          </CardContent>
        </Card>
      </div>

      {/* Attack Types Summary */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Attack Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(stats.attack_types).map(([type, count]) => (
                <div key={type} className="text-center">
                  <div className="text-lg font-bold">{count.toLocaleString()}</div>
                  <div className="text-sm text-muted-foreground">{type}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Search & Filters
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
            <div>
              <select 
                value={attackTypeFilter} 
                onChange={(e) => setAttackTypeFilter(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="all">All Attack Types</option>
                {uniqueAttackTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <select 
                value={threatLevelFilter} 
                onChange={(e) => setThreatLevelFilter(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="all">All Threat Levels</option>
                {uniqueThreatLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
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
                        <Button size="sm" variant="outline" title="View Details">
                          <Eye className="h-3 w-3" />
                        </Button>
                        {threat.pcap_file_path && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadPcap(threat.id, threat.attack_type)}
                            title="Download PCAP"
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
