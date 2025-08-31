"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Play, Database, BarChart3, PieChart, LineChart, Save, History, Code, AlertCircle, CheckCircle } from 'lucide-react'

interface QueryResult {
  columns: string[]
  rows: any[][]
  rowCount: number
  executionTime: number
}

interface SavedQuery {
  id: string
  name: string
  query: string
  createdAt: string
}

export default function SQLQueryDashboard() {
  const [mounted, setMounted] = useState(false)
  const [query, setQuery] = useState('')
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([])
  const [queryName, setQueryName] = useState('')
  const [visualizationType, setVisualizationType] = useState<'table' | 'bar' | 'pie' | 'line'>('table')

  useEffect(() => {
    setMounted(true)
  }, [])

  // Sample queries for real PostgreSQL tables
  const sampleQueries = [
    {
      "name": "Analyse des Menaces par Type",
      "query": "SELECT attack_type, threat_level, COUNT(*) as count, AVG(confidence) as avg_confidence FROM threat_alerts GROUP BY attack_type, threat_level ORDER BY count DESC;"
    },
    {
      "name": "Top IPs Sources d'Attaques",
      "query": "SELECT source_ip, COUNT(*) as attack_count, MAX(confidence) as max_confidence FROM threat_alerts GROUP BY source_ip ORDER BY attack_count DESC LIMIT 10;"
    },
    {
      "name": "Menaces Récentes (24h)",
      "query": "SELECT id, timestamp, source_ip, destination_ip, attack_type, threat_level, confidence, description FROM threat_alerts WHERE timestamp >= NOW() - INTERVAL '24 hours' ORDER BY timestamp DESC;"
    },
    {
      "name": "Statistiques Générales",
      "query": "SELECT COUNT(*) as total_threats, COUNT(DISTINCT source_ip) as unique_sources, AVG(confidence) as avg_confidence, MAX(timestamp) as latest_threat FROM threat_alerts;"
    },
    {
      "name": "Tables Disponibles",
      "query": "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;"
    }
  ]

  const executeQuery = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/database/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
      })
      
      const result = await response.json()
      
      if (result.status === 'success') {
        // Convert result to QueryResult format
        if (result.rows && result.rows.length > 0) {
          const queryResult: QueryResult = {
            columns: result.columns,
            rows: result.rows,
            rowCount: result.rows.length,
            executionTime: 0 // Backend doesn't return execution time yet
          }
          
          setQueryResult(queryResult)
        } else {
          // Handle empty results
          const queryResult: QueryResult = {
            columns: result.columns || ['Result'],
            rows: result.rows || [['No results']],
            rowCount: 0,
            executionTime: 0
          }
          
          setQueryResult(queryResult)
        }
      } else {
        setError(result.detail || 'Query execution failed')
      }
    } catch (err) {
      setError('Network error: Failed to connect to database')
    } finally {
      setLoading(false)
    }
  }

  const saveQuery = () => {
    if (!query.trim() || !queryName.trim()) {
      setError('Please provide both query and name')
      return
    }
    
    const newQuery: SavedQuery = {
      id: `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: queryName,
      query: query,
      createdAt: new Date().toISOString()
    }

    const updated = [...savedQueries, newQuery]
    setSavedQueries(updated)
    localStorage.setItem('savedQueries', JSON.stringify(updated))
    setQueryName('')
    setError(null)
  }

  const loadQuery = (savedQuery: SavedQuery) => {
    setQuery(savedQuery.query)
    setError(null)
  }

  const deleteQuery = (id: string) => {
    const updated = savedQueries.filter(q => q.id !== id)
    setSavedQueries(updated)
    localStorage.setItem('savedQueries', JSON.stringify(updated))
  }

  // Load saved queries from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('savedQueries')
    if (saved) {
      try {
        setSavedQueries(JSON.parse(saved))
      } catch (e) {
        console.error('Error loading saved queries:', e)
      }
    }
  }, [])

  const renderVisualization = () => {
    if (!queryResult || queryResult.rows.length === 0) return null

    switch (visualizationType) {
      case 'bar':
        return renderBarChart()
      case 'pie':
        return renderPieChart()
      case 'line':
        return renderLineChart()
      default:
        return renderTable()
    }
  }

  const renderTable = () => {
    if (!queryResult) return null

    return (
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {queryResult.columns.map((column, index) => (
                <TableHead key={index}>{column}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {queryResult.rows.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <TableCell key={cellIndex} className="font-mono text-sm">
                    {cell !== null ? String(cell) : 'NULL'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    )
  }

  const renderBarChart = () => {
    if (!queryResult || queryResult.columns.length < 2) return <div>Bar chart requires at least 2 columns</div>

    const maxValue = Math.max(...queryResult.rows.map(row => Number(row[1]) || 0))

    return (
      <div className="space-y-2">
        {queryResult.rows.map((row, index) => (
          <div key={index} className="flex items-center gap-4">
            <div className="w-32 text-sm truncate">{String(row[0])}</div>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(Number(row[1]) / maxValue) * 100}%` }}
              >
                <span className="text-white text-xs font-bold">{row[1]}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderPieChart = () => {
    if (!queryResult || queryResult.columns.length < 2) return <div>Pie chart requires at least 2 columns</div>

    const total = queryResult.rows.reduce((sum, row) => sum + (Number(row[1]) || 0), 0)
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

    return (
      <div className="grid grid-cols-2 gap-4">
        <div className="relative w-64 h-64 mx-auto">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            {queryResult.rows.map((row, index) => {
              const percentage = (Number(row[1]) / total) * 100
              const angle = (percentage / 100) * 360
              const startAngle = queryResult.rows.slice(0, index).reduce((sum, r) => sum + ((Number(r[1]) / total) * 360), 0)
              
              const x1 = 100 + 80 * Math.cos((startAngle - 90) * Math.PI / 180)
              const y1 = 100 + 80 * Math.sin((startAngle - 90) * Math.PI / 180)
              const x2 = 100 + 80 * Math.cos((startAngle + angle - 90) * Math.PI / 180)
              const y2 = 100 + 80 * Math.sin((startAngle + angle - 90) * Math.PI / 180)
              
              const largeArcFlag = angle > 180 ? 1 : 0
              
              return (
                <path
                  key={index}
                  d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                  fill={colors[index % colors.length]}
                  stroke="white"
                  strokeWidth="2"
                />
              )
            })}
          </svg>
        </div>
        <div className="space-y-2">
          {queryResult.rows.map((row, index) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: colors[index % colors.length] }}
              />
              <span className="text-sm">{String(row[0])}: {row[1]} ({((Number(row[1]) / total) * 100).toFixed(1)}%)</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderLineChart = () => {
    if (!queryResult || queryResult.columns.length < 2) return <div>Line chart requires at least 2 columns</div>

    const maxValue = Math.max(...queryResult.rows.map(row => Number(row[1]) || 0))
    const points = queryResult.rows.map((row, index) => {
      const x = (index / (queryResult.rows.length - 1)) * 300
      const y = 150 - ((Number(row[1]) / maxValue) * 120)
      return `${x},${y}`
    }).join(' ')

    return (
      <div className="w-full">
        <svg viewBox="0 0 300 200" className="w-full h-64 border">
          <polyline
            points={points}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          {queryResult.rows.map((row, index) => {
            const x = (index / (queryResult.rows.length - 1)) * 300
            const y = 150 - ((Number(row[1]) / maxValue) * 120)
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="4"
                fill="#3b82f6"
              />
            )
          })}
        </svg>
        <div className="flex justify-between text-xs mt-2">
          {queryResult.rows.map((row, index) => (
            <span key={index} className="truncate">{String(row[0])}</span>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {!mounted ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading SQL Query Dashboard...</p>
          </div>
        </div>
      ) : (
      <>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">SQL Query Dashboard</h1>
          <p className="text-muted-foreground">Splunk-like interface for custom database queries and visualizations</p>
        </div>
        <Badge variant="outline">
          <Database className="h-4 w-4 mr-1" />
          PostgreSQL
        </Badge>
      </div>

      <Tabs defaultValue="query" className="space-y-4">
        <TabsList>
          <TabsTrigger value="query">Query Builder</TabsTrigger>
          <TabsTrigger value="samples">Sample Queries</TabsTrigger>
          <TabsTrigger value="saved">Saved Queries ({savedQueries.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="query" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                SQL Query Editor
              </CardTitle>
              <CardDescription>
                Write custom SQL queries to analyze your cybersecurity data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Textarea
                  placeholder="Enter your SQL query here...
Example: SELECT attack_type, COUNT(*) FROM threat_alerts GROUP BY attack_type;"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="font-mono text-sm min-h-32"
                />
              </div>

              <div className="flex gap-2 flex-wrap">
                <Button onClick={executeQuery} disabled={loading}>
                  <Play className="h-4 w-4 mr-1" />
                  {loading ? 'Executing...' : 'Execute Query'}
                </Button>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Query name..."
                    value={queryName}
                    onChange={(e) => setQueryName(e.target.value)}
                    className="px-3 py-2 border rounded-md text-sm"
                  />
                  <Button variant="outline" onClick={saveQuery}>
                    <Save className="h-4 w-4 mr-1" />
                    Save Query
                  </Button>
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-red-700 text-sm">{error}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {queryResult && (
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Query Results
                    </CardTitle>
                    <CardDescription>
                      {queryResult.rowCount} rows returned in {queryResult.executionTime}ms
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={visualizationType === 'table' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setVisualizationType('table')}
                    >
                      Table
                    </Button>
                    <Button
                      variant={visualizationType === 'bar' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setVisualizationType('bar')}
                    >
                      <BarChart3 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={visualizationType === 'pie' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setVisualizationType('pie')}
                    >
                      <PieChart className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={visualizationType === 'line' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setVisualizationType('line')}
                    >
                      <LineChart className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {renderVisualization()}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="samples" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sample Queries</CardTitle>
              <CardDescription>Pre-built queries to get you started with data analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {sampleQueries.map((sample, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold">{sample.name}</h3>
                      <Button size="sm" onClick={() => setQuery(sample.query)}>
                        Load Query
                      </Button>
                    </div>
                    <pre className="text-sm bg-gray-100 p-2 rounded font-mono overflow-x-auto">
                      {sample.query}
                    </pre>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saved" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Saved Queries
              </CardTitle>
              <CardDescription>Your custom saved queries</CardDescription>
            </CardHeader>
            <CardContent>
              {savedQueries.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No saved queries yet. Create and save queries from the Query Builder tab.
                </div>
              ) : (
                <div className="space-y-4">
                  {savedQueries.map((savedQuery) => (
                    <div key={savedQuery.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold">{savedQuery.name}</h3>
                          <p className="text-sm text-muted-foreground">
                            Created: {mounted ? new Date(savedQuery.createdAt).toLocaleString() : savedQuery.createdAt}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => loadQuery(savedQuery)}>
                            Load
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => deleteQuery(savedQuery.id)}>
                            Delete
                          </Button>
                        </div>
                      </div>
                      <pre className="text-sm bg-gray-100 p-2 rounded font-mono overflow-x-auto">
                        {savedQuery.query}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </>
      )}
    </div>
  )
}
