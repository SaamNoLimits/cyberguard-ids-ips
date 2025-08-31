"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Database, Download, Search, RefreshCw, Eye, Filter, BarChart3, PieChart, Activity, Server, TableProperties } from 'lucide-react'

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

interface DatabaseTable {
  table_name: string
  row_count: number
  size_bytes: number
  columns: Array<{
    column_name: string
    data_type: string
    is_nullable: boolean
  }>
}

export default function AdvancedDatabaseDashboard() {
  const [threats, setThreats] = useState<ThreatRecord[]>([])
  const [filteredThreats, setFilteredThreats] = useState<ThreatRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [attackTypeFilter, setAttackTypeFilter] = useState('all')
  const [threatLevelFilter, setThreatLevelFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(0)
  const [limit] = useState(50)
  const [stats, setStats] = useState<DatabaseStats | null>(null)
  const [databaseTables, setDatabaseTables] = useState<DatabaseTable[]>([])
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([])

  const fetchDatabaseSchema = async () => {
    try {
      // Simulate database schema info - you can create an API endpoint for this
      const mockTables: DatabaseTable[] = [
        {
          table_name: 'threat_alerts',
          row_count: stats?.total_threats || 0,
          size_bytes: 1024 * 1024 * 50, // 50MB
          columns: [
            { column_name: 'id', data_type: 'UUID', is_nullable: false },
            { column_name: 'timestamp', data_type: 'TIMESTAMP', is_nullable: false },
            { column_name: 'source_ip', data_type: 'VARCHAR(45)', is_nullable: false },
            { column_name: 'destination_ip', data_type: 'VARCHAR(45)', is_nullable: false },
            { column_name: 'attack_type', data_type: 'VARCHAR(50)', is_nullable: false },
            { column_name: 'threat_level', data_type: 'VARCHAR(20)', is_nullable: false },
            { column_name: 'confidence', data_type: 'FLOAT', is_nullable: false },
            { column_name: 'description', data_type: 'TEXT', is_nullable: true },
            { column_name: 'blocked', data_type: 'BOOLEAN', is_nullable: false },
            { column_name: 'pcap_file_path', data_type: 'VARCHAR(255)', is_nullable: true },
            { column_name: 'packet_count', data_type: 'INTEGER', is_nullable: true },
            { column_name: 'bytes_transferred', data_type: 'BIGINT', is_nullable: true },
          ]
        },
        {
          table_name: 'pcap_files',
          row_count: stats?.pcap_files_count || 0,
          size_bytes: 1024 * 1024 * 200, // 200MB
          columns: [
            { column_name: 'id', data_type: 'UUID', is_nullable: false },
            { column_name: 'threat_id', data_type: 'UUID', is_nullable: false },
            { column_name: 'file_path', data_type: 'VARCHAR(255)', is_nullable: false },
            { column_name: 'file_size', data_type: 'BIGINT', is_nullable: false },
            { column_name: 'created_at', data_type: 'TIMESTAMP', is_nullable: false },
            { column_name: 'sha256_hash', data_type: 'VARCHAR(64)', is_nullable: false },
          ]
        },
        {
          table_name: 'network_devices',
          row_count: 25,
          size_bytes: 1024 * 50, // 50KB
          columns: [
            { column_name: 'id', data_type: 'UUID', is_nullable: false },
            { column_name: 'ip_address', data_type: 'VARCHAR(45)', is_nullable: false },
            { column_name: 'mac_address', data_type: 'VARCHAR(17)', is_nullable: true },
            { column_name: 'device_type', data_type: 'VARCHAR(50)', is_nullable: true },
            { column_name: 'first_seen', data_type: 'TIMESTAMP', is_nullable: false },
            { column_name: 'last_seen', data_type: 'TIMESTAMP', is_nullable: false },
          ]
        }
      ]
      setDatabaseTables(mockTables)
    } catch (error) {
      console.error('Error fetching database schema:', error)
    }
  }

  const generateTimeSeriesData = () => {
    if (!threats.length) return

    // Group threats by hour for the last 24 hours
    const hourlyData: Record<string, number> = {}
    const now = new Date()
    
    // Initialize last 24 hours
    for (let i = 23; i >= 0; i--) {
      const hour = new Date(now.getTime() - i * 60 * 60 * 1000)
      const hourKey = hour.toISOString().slice(0, 13) + ':00'
      hourlyData[hourKey] = 0
    }

    // Count threats per hour
    threats.forEach(threat => {
      const threatHour = new Date(threat.timestamp).toISOString().slice(0, 13) + ':00'
      if (hourlyData.hasOwnProperty(threatHour)) {
        hourlyData[threatHour]++
      }
    })

    const chartData = Object.entries(hourlyData).map(([hour, count]) => ({
      time: new Date(hour).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      threats: count
    }))

    setTimeSeriesData(chartData)
  }

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
      // L'API retourne directement un tableau
      const threats = Array.isArray(threatsData) ? threatsData : (threatsData.threats || [])
      setThreats(threats)
      setFilteredThreats(threats)
      
      // Generate time series data
      generateTimeSeriesData()
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter and search logic
  useEffect(() => {
    let filtered = threats

    if (searchTerm) {
      filtered = filtered.filter(threat => 
        threat.source_ip.includes(searchTerm) ||
        threat.destination_ip.includes(searchTerm) ||
        threat.attack_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        threat.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (attackTypeFilter !== 'all') {
      filtered = filtered.filter(threat => threat.attack_type === attackTypeFilter)
    }

    if (threatLevelFilter !== 'all') {
      filtered = filtered.filter(threat => threat.threat_level === threatLevelFilter)
    }

    setFilteredThreats(filtered)
    setCurrentPage(0)
  }, [searchTerm, attackTypeFilter, threatLevelFilter, threats])

  useEffect(() => {
    generateTimeSeriesData()
  }, [threats])

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
      case 'CRITICAL': return 'bg-red-500 text-white'
      case 'HIGH': return 'bg-orange-500 text-white'
      case 'MEDIUM': return 'bg-yellow-500 text-black'
      case 'LOW': return 'bg-green-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const uniqueAttackTypes = [...new Set(threats.map(t => t.attack_type))]
  const uniqueThreatLevels = [...new Set(threats.map(t => t.threat_level))]
  const paginatedThreats = filteredThreats.slice(currentPage * limit, (currentPage + 1) * limit)

  useEffect(() => {
    fetchAllData()
    fetchDatabaseSchema()
    const interval = setInterval(fetchAllData, 30000)
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
          <h1 className="text-3xl font-bold">Advanced Database Dashboard</h1>
          <p className="text-muted-foreground">Complete database analysis with visualizations and schema</p>
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

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
          <TabsTrigger value="database-schema">Database Schema</TabsTrigger>
          <TabsTrigger value="threat-records">Threat Records</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Total Threats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_threats?.toLocaleString() || 0}</div>
                <p className="text-xs text-muted-foreground">All time records</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Recent (24h)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.recent_threats_24h?.toLocaleString() || 0}</div>
                <p className="text-xs text-muted-foreground">Last 24 hours</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Server className="h-4 w-4" />
                  PCAP Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.pcap_files_count || 0}</div>
                <p className="text-xs text-muted-foreground">Forensic evidence</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Attack Types
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{uniqueAttackTypes.length}</div>
                <p className="text-xs text-muted-foreground">Different types</p>
              </CardContent>
            </Card>
          </div>

          {/* Attack Distribution */}
          {stats && (
            <Card>
              <CardHeader>
                <CardTitle>Attack Type Distribution</CardTitle>
                <CardDescription>Breakdown of detected attack types</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(stats.attack_types).map(([type, count]) => (
                    <div key={type} className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-orange-500">{count.toLocaleString()}</div>
                      <div className="text-sm font-medium">{type}</div>
                      <div className="text-xs text-muted-foreground">
                        {((count / stats.total_threats) * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Threat Level Distribution */}
          {stats && (
            <Card>
              <CardHeader>
                <CardTitle>Threat Level Distribution</CardTitle>
                <CardDescription>Security risk levels of detected threats</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(stats.threat_levels).map(([level, count]) => (
                    <div key={level} className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-red-500">{count.toLocaleString()}</div>
                      <Badge className={getThreatLevelColor(level)} variant="secondary">
                        {level}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {((count / stats.total_threats) * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="visualizations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Threat Timeline (Last 24 Hours)</CardTitle>
              <CardDescription>Hourly threat detection over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 w-full">
                {timeSeriesData.length > 0 ? (
                  <div className="grid grid-cols-12 gap-1 h-full">
                    {timeSeriesData.map((data, index) => (
                      <div key={index} className="flex flex-col justify-end items-center">
                        <div 
                          className="bg-blue-500 w-full rounded-t"
                          style={{ 
                            height: `${Math.max((data.threats / Math.max(...timeSeriesData.map(d => d.threats))) * 200, 2)}px` 
                          }}
                          title={`${data.time}: ${data.threats} threats`}
                        />
                        <div className="text-xs mt-1 transform -rotate-45 origin-top-left">
                          {data.time}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    No time series data available
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Top Source IPs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(
                    threats.reduce((acc, threat) => {
                      acc[threat.source_ip] = (acc[threat.source_ip] || 0) + 1
                      return acc
                    }, {} as Record<string, number>)
                  )
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 10)
                    .map(([ip, count]) => (
                      <div key={ip} className="flex justify-between items-center">
                        <span className="font-mono text-sm">{ip}</span>
                        <Badge variant="outline">{count}</Badge>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Destination IPs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(
                    threats.reduce((acc, threat) => {
                      acc[threat.destination_ip] = (acc[threat.destination_ip] || 0) + 1
                      return acc
                    }, {} as Record<string, number>)
                  )
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 10)
                    .map(([ip, count]) => (
                      <div key={ip} className="flex justify-between items-center">
                        <span className="font-mono text-sm">{ip}</span>
                        <Badge variant="outline">{count}</Badge>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="database-schema" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TableProperties className="h-5 w-5" />
                Database Schema Overview
              </CardTitle>
              <CardDescription>Complete database structure and table information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {databaseTables.map((table) => (
                  <div key={table.table_name} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold">{table.table_name}</h3>
                      <div className="flex gap-4 text-sm text-muted-foreground">
                        <span>{table.row_count.toLocaleString()} rows</span>
                        <span>{formatBytes(table.size_bytes)}</span>
                      </div>
                    </div>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Column Name</TableHead>
                            <TableHead>Data Type</TableHead>
                            <TableHead>Nullable</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {table.columns.map((column) => (
                            <TableRow key={column.column_name}>
                              <TableCell className="font-mono">{column.column_name}</TableCell>
                              <TableCell>
                                <Badge variant="outline">{column.data_type}</Badge>
                              </TableCell>
                              <TableCell>
                                <Badge variant={column.is_nullable ? "secondary" : "default"}>
                                  {column.is_nullable ? "YES" : "NO"}
                                </Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="threat-records" className="space-y-4">
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
              <CardTitle>Threat Records ({filteredThreats.length.toLocaleString()} threats)</CardTitle>
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
        </TabsContent>
      </Tabs>
    </div>
  )
}
