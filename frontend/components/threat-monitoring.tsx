"use client"

import React, { useState, useEffect, useMemo } from 'react'
import { apiClient, WS_URL } from '@/lib/api'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertTriangle, ShieldCheck, ArrowUpDown, Search } from 'lucide-react'
import { ThreatDetailsModal } from './threat-details-modal'

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
  protocol?: string
  source_port?: number
  destination_port?: number
  packet_size?: number
  tcp_flags?: number
  ttl?: number
  raw_data?: {
    protocol: number
    packet_size: number
    ttl: number
    source_port?: number
    destination_port?: number
    tcp_flags?: number
    fin_flag?: number
    syn_flag?: number
    rst_flag?: number
    psh_flag?: number
    ack_flag?: number
    urg_flag?: number
    window_size?: number
    icmp_type?: number
    icmp_code?: number
    udp_length?: number
  }
}

type SortKey = keyof ThreatAlert | ''

export default function ThreatMonitoring() {
  const [threats, setThreats] = useState<ThreatAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('timestamp')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [selectedThreatId, setSelectedThreatId] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    loadThreats()
    
    // Set up WebSocket for real-time threat alerts
    const wsUrl = WS_URL
    console.log('Attempting WebSocket connection to:', wsUrl)
    
    let ws: WebSocket
    try {
      ws = new WebSocket(wsUrl)
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      return
    }
    
    ws.onopen = () => {
      console.log('WebSocket connected successfully for threat monitoring')
    }
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (message.type === 'threat_alert') {
          const rawData = message.data.raw_data || {}
          const protocolMap: { [key: number]: string } = { 1: 'ICMP', 6: 'TCP', 17: 'UDP' }
          
          const newThreat: ThreatAlert = {
            id: message.data.id,
            timestamp: message.data.timestamp,
            source_ip: message.data.source_ip,
            destination_ip: message.data.destination_ip,
            attack_type: message.data.attack_type,
            threat_level: message.data.threat_level.toLowerCase(),
            confidence: message.data.confidence,
            description: message.data.description,
            blocked: message.data.blocked,
            protocol: protocolMap[rawData.protocol] || 'Unknown',
            source_port: rawData.source_port,
            destination_port: rawData.destination_port,
            packet_size: rawData.packet_size,
            tcp_flags: rawData.tcp_flags,
            ttl: rawData.ttl,
            raw_data: rawData
          }
          
          // Add new threat to the beginning of the list
          setThreats(prevThreats => [newThreat, ...prevThreats.slice(0, 499)])
          
          // Show notification for high/critical threats
          if (newThreat.threat_level === 'high' || newThreat.threat_level === 'critical') {
            console.warn(`🚨 ${newThreat.attack_type} detected from ${newThreat.source_ip}`)
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket connection error. Check if backend server is running on port 8000:', error)
      console.log('Expected WebSocket URL:', wsUrl)
    }
    
    ws.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason)
      if (event.code !== 1000) {
        console.warn('WebSocket closed unexpectedly. Attempting to reconnect in 5 seconds...')
        setTimeout(() => {
          // Could implement reconnection logic here
        }, 5000)
      }
    }
    
    // Cleanup WebSocket on component unmount
    return () => {
      ws.close()
    }
  }, [])

  const loadThreats = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await apiClient.getRecentThreats(500) // Fetch more for filtering
      setThreats(data)
    } catch (err) {
      setError('Failed to fetch threat data. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const handleThreatClick = (threatId: string) => {
    setSelectedThreatId(threatId)
    setIsModalOpen(true)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedThreatId(null)
  }

  const handleThreatBlock = (threatId: string) => {
    // Update the threat status in the local state
    setThreats(prev => prev.map(threat => 
      threat.id === threatId ? { ...threat, blocked: true } : threat
    ))
  }

  const handleThreatUnblock = (threatId: string) => {
    // Update the threat status in the local state
    setThreats(prev => prev.map(threat => 
      threat.id === threatId ? { ...threat, blocked: false } : threat
    ))
  }

  const filteredAndSortedThreats = useMemo(() => {
    let filtered = threats.filter(threat => 
      Object.values(threat).some(value => 
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )

    if (sortKey) {
      filtered.sort((a, b) => {
        const aValue = a[sortKey] ?? ''
        const bValue = b[sortKey] ?? ''
        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
        if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
        return 0
      })
    }

    return filtered
  }, [threats, searchTerm, sortKey, sortDirection])

  const getThreatLevelBadge = (level: string) => {
    const colorMapping = {
      'low': 'bg-blue-500',
      'medium': 'bg-yellow-500',
      'high': 'bg-orange-500',
      'critical': 'bg-red-500',
    }
    return <Badge className={`${colorMapping[level as keyof typeof colorMapping] || 'bg-gray-500'} text-white`}>{level}</Badge>
  }

  const stats = useMemo(() => {
    const attackTypes = threats.reduce((acc, threat) => {
      acc[threat.attack_type] = (acc[threat.attack_type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    const protocols = threats.reduce((acc, threat) => {
      const protocol = threat.protocol || 'Unknown'
      acc[protocol] = (acc[protocol] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    const avgConfidence = threats.length > 0 
      ? threats.reduce((sum, threat) => sum + threat.confidence, 0) / threats.length 
      : 0
    
    return {
      total: threats.length,
      blocked: threats.filter(t => t.blocked).length,
      critical: threats.filter(t => t.threat_level === 'critical').length,
      high: threats.filter(t => t.threat_level === 'high').length,
      medium: threats.filter(t => t.threat_level === 'medium').length,
      low: threats.filter(t => t.threat_level === 'low').length,
      attackTypes,
      protocols,
      avgConfidence,
      highConfidence: threats.filter(t => t.confidence > 0.8).length
    }
  }, [threats])

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Threat Monitoring</h1>
          <p className="text-muted-foreground">Live feed of detected security threats and incidents</p>
        </div>
        <Button onClick={loadThreats} disabled={isLoading} variant="outline" size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Threats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">Detected by AI Model</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Blocked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.blocked}</div>
            <p className="text-xs text-muted-foreground">{stats.total > 0 ? ((stats.blocked / stats.total) * 100).toFixed(1) : 0}% blocked</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Critical/High</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.critical + stats.high}</div>
            <p className="text-xs text-muted-foreground">{stats.critical} critical, {stats.high} high</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(stats.avgConfidence * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">{stats.highConfidence} high confidence</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Top Attack</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-bold">
              {Object.entries(stats.attackTypes).sort(([,a], [,b]) => b - a)[0]?.[0] || 'None'}
            </div>
            <p className="text-xs text-muted-foreground">
              {Object.entries(stats.attackTypes).sort(([,a], [,b]) => b - a)[0]?.[1] || 0} occurrences
            </p>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Attack Types Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(stats.attackTypes)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 5)
                .map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{type}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 bg-blue-500 rounded-full" 
                        style={{ width: `${(count / stats.total) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Protocol Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(stats.protocols)
                .sort(([,a], [,b]) => b - a)
                .map(([protocol, count]) => (
                <div key={protocol} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{protocol}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 bg-green-500 rounded-full" 
                        style={{ width: `${(count / stats.total) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Threat Feed</CardTitle>
          <CardDescription>Detailed list of all detected threats.</CardDescription>
          <div className="flex items-center space-x-4 pt-4">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input 
                placeholder="Search threats..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-full"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead onClick={() => handleSort('timestamp')}>Timestamp <ArrowUpDown className="h-4 w-4 inline" /></TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Destination</TableHead>
                  <TableHead>Attack Type</TableHead>
                  <TableHead>Protocol</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead onClick={() => handleSort('threat_level')}>Severity <ArrowUpDown className="h-4 w-4 inline" /></TableHead>
                  <TableHead>Packet Info</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow><TableCell colSpan={9} className="text-center h-64">Loading threats...</TableCell></TableRow>
                ) : filteredAndSortedThreats.map((threat) => (
                  <TableRow 
                    key={threat.id} 
                    className={`cursor-pointer hover:bg-gray-50 ${threat.threat_level === 'critical' ? 'bg-red-50' : threat.threat_level === 'high' ? 'bg-orange-50' : ''}`}
                    onClick={() => handleThreatClick(threat.id)}
                  >
                    <TableCell className="font-mono text-sm">
                      {new Date(threat.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <div className="font-mono text-sm">
                        <div>{threat.source_ip}</div>
                        {threat.source_port && <div className="text-xs text-gray-500">:{threat.source_port}</div>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-mono text-sm">
                        <div>{threat.destination_ip}</div>
                        {threat.destination_port && <div className="text-xs text-gray-500">:{threat.destination_port}</div>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-semibold">
                        {threat.attack_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {threat.protocol || 'Unknown'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="text-sm font-semibold">
                          {(threat.confidence * 100).toFixed(1)}%
                        </div>
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              threat.confidence > 0.8 ? 'bg-red-500' : 
                              threat.confidence > 0.6 ? 'bg-orange-500' : 'bg-yellow-500'
                            }`}
                            style={{ width: `${threat.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{getThreatLevelBadge(threat.threat_level)}</TableCell>
                    <TableCell>
                      <div className="text-xs space-y-1">
                        {threat.packet_size && <div>Size: {threat.packet_size}B</div>}
                        {threat.ttl && <div>TTL: {threat.ttl}</div>}
                        {threat.tcp_flags && <div>TCP Flags: 0x{threat.tcp_flags.toString(16)}</div>}
                        {threat.raw_data?.window_size && <div>Window: {threat.raw_data.window_size}</div>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={threat.blocked ? 'default' : 'destructive'}>
                        {threat.blocked ? <ShieldCheck className="h-4 w-4 mr-1" /> : <AlertTriangle className="h-4 w-4 mr-1" />}
                        {threat.blocked ? 'Blocked' : 'Detected'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
      
      {/* Threat Details Modal */}
      {selectedThreatId && (
        <ThreatDetailsModal
          threatId={selectedThreatId}
          isOpen={isModalOpen}
          onClose={handleModalClose}
          onBlock={handleThreatBlock}
          onUnblock={handleThreatUnblock}
        />
      )}
    </div>
  )
}
