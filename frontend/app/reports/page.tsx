"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  FileText, 
  Download, 
  Calendar, 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Plus,
  Eye,
  Filter,
  RefreshCw,
  CheckCircle,
  Clock,
  Users,
  Activity
} from 'lucide-react'
import { apiClient } from '@/lib/api'

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

interface IncidentReport {
  id: string
  title: string
  type: string
  severity: string
  status: string
  createdAt: string
  description: string
  affectedSystems: string[]
  threats: ThreatAlert[]
  analyst: string
  resolution?: string
}

export default function ReportsPage() {
  const [mounted, setMounted] = useState(false)
  const [threats, setThreats] = useState<ThreatAlert[]>([])
  const [reports, setReports] = useState<IncidentReport[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [loading, setLoading] = useState(true)
  const [newReport, setNewReport] = useState({
    title: '',
    type: 'incident',
    severity: 'medium',
    description: '',
    affectedSystems: '',
    analyst: 'Security Analyst'
  })
  const [selectedThreats, setSelectedThreats] = useState<string[]>([])
  const [filter, setFilter] = useState({
    dateRange: '24h',
    severity: 'all',
    type: 'all'
  })

  useEffect(() => {
    setMounted(true)
    loadThreats()
    loadReports()
  }, [])

  const loadThreats = async () => {
    try {
      const response = await apiClient.getRecentThreats(50)
      setThreats(response || [])
    } catch (error) {
      console.error('Failed to load threats:', error)
    }
  }

  const loadReports = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/reports?limit=100')
      if (response.ok) {
        const data = await response.json()
        setReports(data.reports || [])
      } else {
        console.error('Failed to load reports:', response.statusText)
      }
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveReports = async (reportData: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
      })
      
      if (response.ok) {
        // Reload reports after successful creation
        await loadReports()
        return true
      } else {
        console.error('Failed to save report:', response.statusText)
        return false
      }
    } catch (error) {
      console.error('Error saving report:', error)
      return false
    }
  }

  const generateReport = async () => {
    if (!newReport.title || !newReport.description) {
      alert('Please fill in all required fields')
      return
    }

    setIsGenerating(true)
    
    const reportThreats = threats.filter(t => selectedThreats.includes(t.id))
    
    const reportData = {
      title: newReport.title,
      type: newReport.type,
      severity: newReport.severity,
      status: 'open',
      description: newReport.description,
      affectedSystems: newReport.affectedSystems.split(',').map(s => s.trim()).filter(Boolean),
      threats: reportThreats,
      analyst: newReport.analyst,
      metadata: {
        createdBy: 'Web Interface',
        threatCount: reportThreats.length
      }
    }

    const success = await saveReports(reportData)
    
    if (success) {
      // Reset form
      setNewReport({
        title: '',
        type: 'incident',
        severity: 'medium', 
        description: '',
        affectedSystems: '',
        analyst: 'Security Analyst'
      })
      setSelectedThreats([])
    } else {
      alert('Failed to create report. Please try again.')
    }
    
    setTimeout(() => setIsGenerating(false), 1500)
  }

  const downloadReport = (report: IncidentReport, format: 'pdf' | 'json') => {
    const content = {
      ...report,
      generatedAt: new Date().toISOString(),
      summary: {
        totalThreats: report.threats.length,
        highSeverityThreats: report.threats.filter(t => t.threat_level === 'HIGH' || t.threat_level === 'CRITICAL').length,
        blockedThreats: report.threats.filter(t => t.blocked).length,
        attackTypes: [...new Set(report.threats.map(t => t.attack_type))]
      }
    }
    
    const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.id}_${format}.${format === 'pdf' ? 'json' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  }

  const filteredThreats = threats.filter(threat => {
    if (filter.severity !== 'all' && threat.threat_level !== filter.severity.toUpperCase()) return false
    if (filter.type !== 'all' && threat.attack_type !== filter.type) return false
    return true
  })

  if (!mounted) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading Reports Dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Incident Reports</h1>
          <p className="text-muted-foreground">Generate detailed security incident reports and analysis</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Report
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Generate Incident Report</DialogTitle>
              <DialogDescription>
                Create a comprehensive incident report with threat analysis
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="title">Report Title *</Label>
                  <Input
                    id="title"
                    value={newReport.title}
                    onChange={(e) => setNewReport({...newReport, title: e.target.value})}
                    placeholder="Security Incident - Network Breach"
                  />
                </div>
                <div>
                  <Label htmlFor="analyst">Analyst</Label>
                  <Input
                    id="analyst"
                    value={newReport.analyst}
                    onChange={(e) => setNewReport({...newReport, analyst: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="type">Report Type</Label>
                  <Select value={newReport.type} onValueChange={(value) => setNewReport({...newReport, type: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incident">Security Incident</SelectItem>
                      <SelectItem value="investigation">Investigation</SelectItem>
                      <SelectItem value="assessment">Risk Assessment</SelectItem>
                      <SelectItem value="compliance">Compliance Report</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="severity">Severity</Label>
                  <Select value={newReport.severity} onValueChange={(value) => setNewReport({...newReport, severity: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Selected Threats</Label>
                  <div className="text-sm text-muted-foreground mt-1">
                    {selectedThreats.length} threats selected
                  </div>
                </div>
              </div>
              
              <div>
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  value={newReport.description}
                  onChange={(e) => setNewReport({...newReport, description: e.target.value})}
                  placeholder="Detailed description of the security incident, including timeline, impact, and initial findings..."
                  rows={4}
                />
              </div>
              
              <div>
                <Label htmlFor="systems">Affected Systems</Label>
                <Input
                  id="systems"
                  value={newReport.affectedSystems}
                  onChange={(e) => setNewReport({...newReport, affectedSystems: e.target.value})}
                  placeholder="Server-01, Database-Main, Network-DMZ (comma separated)"
                />
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-4">
                  <Label>Select Related Threats</Label>
                  <div className="flex gap-2">
                    <Select value={filter.severity} onValueChange={(value) => setFilter({...filter, severity: value})}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Severity</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button onClick={loadThreats} size="sm" variant="outline">
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="max-h-60 overflow-y-auto border rounded p-2 space-y-2">
                  {filteredThreats.map((threat) => (
                    <div key={threat.id} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={selectedThreats.includes(threat.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedThreats([...selectedThreats, threat.id])
                          } else {
                            setSelectedThreats(selectedThreats.filter(id => id !== threat.id))
                          }
                        }}
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant={threat.threat_level === 'HIGH' || threat.threat_level === 'CRITICAL' ? 'destructive' : 'secondary'}>
                            {threat.threat_level}
                          </Badge>
                          <span className="text-sm font-medium">{threat.attack_type}</span>
                          <span className="text-xs text-muted-foreground">{threat.source_ip}</span>
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{threat.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => {
                  setNewReport({
                    title: '',
                    type: 'incident',
                    severity: 'medium',
                    description: '',
                    affectedSystems: '',
                    analyst: 'Security Analyst'
                  })
                  setSelectedThreats([])
                }}>Cancel</Button>
                <Button onClick={generateReport} disabled={isGenerating}>
                  {isGenerating ? (
                    <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Generating...</>
                  ) : (
                    <><FileText className="h-4 w-4 mr-2" />Generate Report</>
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <h3 className="text-lg font-medium mb-2">Loading Reports...</h3>
            <p className="text-muted-foreground">Fetching incident reports from database</p>
          </CardContent>
        </Card>
      ) : reports.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No Reports Generated</h3>
            <p className="text-muted-foreground mb-4">Create your first incident report to get started</p>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Report
                </Button>
              </DialogTrigger>
            </Dialog>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {reports.map((report) => (
            <Card key={report.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-8 w-8 text-orange-500" />
                    <div>
                      <CardTitle>{report.title}</CardTitle>
                      <CardDescription>Created by {report.analyst} • {new Date(report.createdAt).toLocaleString()}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={report.severity === 'critical' || report.severity === 'high' ? 'destructive' : 'secondary'}>
                      {report.severity.toUpperCase()}
                    </Badge>
                    <Badge variant={report.status === 'open' ? 'destructive' : 'default'}>
                      {report.status === 'open' ? <Clock className="h-3 w-3 mr-1" /> : <CheckCircle className="h-3 w-3 mr-1" />}
                      {report.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm">{report.description}</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Type:</span>
                      <div className="font-medium capitalize">{report.type}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Threats:</span>
                      <div className="font-medium">{report.threats.length}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Systems:</span>
                      <div className="font-medium">{report.affectedSystems.length}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status:</span>
                      <div className="font-medium capitalize">{report.status}</div>
                    </div>
                  </div>
                  
                  {report.affectedSystems.length > 0 && (
                    <div>
                      <span className="text-sm text-muted-foreground">Affected Systems:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {report.affectedSystems.map((system, idx) => (
                          <Badge key={idx} variant="outline">{system}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => downloadReport(report, 'json')}>
                      <Download className="h-4 w-4 mr-1" />
                      Download JSON
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => downloadReport(report, 'pdf')}>
                      <Download className="h-4 w-4 mr-1" />
                      Export Report
                    </Button>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader>
                          <DialogTitle>{report.title}</DialogTitle>
                          <DialogDescription>Detailed incident report analysis</DialogDescription>
                        </DialogHeader>
                        <div className="space-y-6">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-medium mb-2">Report Information</h4>
                              <div className="space-y-2 text-sm">
                                <div><strong>ID:</strong> {report.id}</div>
                                <div><strong>Type:</strong> {report.type}</div>
                                <div><strong>Severity:</strong> {report.severity}</div>
                                <div><strong>Status:</strong> {report.status}</div>
                                <div><strong>Analyst:</strong> {report.analyst}</div>
                                <div><strong>Created:</strong> {new Date(report.createdAt).toLocaleString()}</div>
                              </div>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Summary Statistics</h4>
                              <div className="space-y-2 text-sm">
                                <div><strong>Total Threats:</strong> {report.threats.length}</div>
                                <div><strong>High/Critical:</strong> {report.threats.filter(t => t.threat_level === 'HIGH' || t.threat_level === 'CRITICAL').length}</div>
                                <div><strong>Blocked:</strong> {report.threats.filter(t => t.blocked).length}</div>
                                <div><strong>Attack Types:</strong> {[...new Set(report.threats.map(t => t.attack_type))].length}</div>
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-medium mb-2">Description</h4>
                            <p className="text-sm bg-gray-50 p-3 rounded">{report.description}</p>
                          </div>
                          
                          {report.threats.length > 0 && (
                            <div>
                              <h4 className="font-medium mb-2">Related Threats ({report.threats.length})</h4>
                              <div className="max-h-60 overflow-y-auto space-y-2">
                                {report.threats.map((threat) => (
                                  <div key={threat.id} className="border rounded p-3 text-sm">
                                    <div className="flex items-center justify-between mb-2">
                                      <div className="flex items-center gap-2">
                                        <Badge variant={threat.threat_level === 'HIGH' || threat.threat_level === 'CRITICAL' ? 'destructive' : 'secondary'}>
                                          {threat.threat_level}
                                        </Badge>
                                        <span className="font-medium">{threat.attack_type}</span>
                                      </div>
                                      <Badge variant={threat.blocked ? 'default' : 'destructive'}>
                                        {threat.blocked ? 'Blocked' : 'Detected'}
                                      </Badge>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                                      <div><strong>Source:</strong> {threat.source_ip}</div>
                                      <div><strong>Destination:</strong> {threat.destination_ip}</div>
                                      <div><strong>Confidence:</strong> {threat.confidence}%</div>
                                      <div><strong>Time:</strong> {new Date(threat.timestamp).toLocaleString()}</div>
                                    </div>
                                    <p className="text-xs mt-2">{threat.description}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
