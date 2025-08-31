"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Database, 
  Table as TableIcon, 
  Play, 
  Code, 
  Terminal, 
  RefreshCw, 
  Eye, 
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText
} from 'lucide-react'

interface DatabaseTable {
  tablename: string
  row_count: number
  size: string
  tableowner: string
  hasindexes: boolean
  hasrules: boolean
  hastriggers: boolean
}

interface TableColumn {
  column_name: string
  data_type: string
  is_nullable: string
  column_default: string | null
  character_maximum_length: number | null
}

interface QueryResult {
  success: boolean
  result: any
  execution_time: number
  error?: string
}

interface QueryHistory {
  id: number
  query_type: string
  query_text: string
  result: string
  execution_time: number
  timestamp: string
  success: boolean
}

export default function CompleteDatabaseExplorer() {
  const [tables, setTables] = useState<DatabaseTable[]>([])
  const [selectedTable, setSelectedTable] = useState<string>('')
  const [tableColumns, setTableColumns] = useState<TableColumn[]>([])
  const [tableData, setTableData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  
  // SQL Query State
  const [sqlQuery, setSqlQuery] = useState('')
  const [sqlResult, setSqlResult] = useState<QueryResult | null>(null)
  const [sqlLoading, setSqlLoading] = useState(false)
  
  // Python Script State
  const [pythonCode, setPythonCode] = useState('')
  const [pythonResult, setPythonResult] = useState<QueryResult | null>(null)
  const [pythonLoading, setPythonLoading] = useState(false)
  
  // Query History
  const [queryHistory, setQueryHistory] = useState<QueryHistory[]>([])

  useEffect(() => {
    loadTables()
    loadQueryHistory()
  }, [])

  const loadTables = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/database/tables')
      const data = await response.json()
      setTables(data)
    } catch (error) {
      console.error('Error loading tables:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTableDetails = async (tableName: string) => {
    try {
      setLoading(true)
      setSelectedTable(tableName)
      
      // Load columns
      const columnsResponse = await fetch(`http://localhost:8000/api/database/table/${tableName}/columns`)
      const columns = await columnsResponse.json()
      setTableColumns(columns)
      
      // Load data
      const dataResponse = await fetch(`http://localhost:8000/api/database/table/${tableName}/data?limit=50`)
      const data = await dataResponse.json()
      setTableData(data)
    } catch (error) {
      console.error('Error loading table details:', error)
    } finally {
      setLoading(false)
    }
  }

  const executeSqlQuery = async () => {
    if (!sqlQuery.trim()) return
    
    try {
      setSqlLoading(true)
      const response = await fetch('http://localhost:8000/api/sql/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sqlQuery })
      })
      const result = await response.json()
      setSqlResult(result)
      loadQueryHistory() // Refresh history
    } catch (error) {
      setSqlResult({
        success: false,
        result: null,
        execution_time: 0,
        error: 'Network error'
      })
    } finally {
      setSqlLoading(false)
    }
  }

  const executePythonScript = async () => {
    if (!pythonCode.trim()) return
    
    try {
      setPythonLoading(true)
      const response = await fetch('http://localhost:8000/api/python/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: pythonCode })
      })
      const result = await response.json()
      setPythonResult(result)
      loadQueryHistory() // Refresh history
    } catch (error) {
      setPythonResult({
        success: false,
        result: null,
        execution_time: 0,
        error: 'Network error'
      })
    } finally {
      setPythonLoading(false)
    }
  }

  const loadQueryHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/query/history?limit=10')
      const data = await response.json()
      setQueryHistory(data)
    } catch (error) {
      console.error('Error loading query history:', error)
    }
  }

  const setSampleSqlQuery = () => {
    setSqlQuery(`-- Analyse des menaces par type et niveau
SELECT 
    attack_type,
    threat_level,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen
FROM threats 
GROUP BY attack_type, threat_level 
ORDER BY count DESC;`)
  }

  const setSamplePythonScript = () => {
    setPythonCode(`# Analyse avancée des menaces avec Python
import json
from datetime import datetime, timedelta

# Simulation d'analyse de sécurité
print("=== ANALYSE DE SÉCURITÉ AVANCÉE ===")

# Données simulées (dans un vrai script, on se connecterait à la DB)
threat_data = {
    "total_threats": 10,
    "high_risk": 9,
    "medium_risk": 1,
    "attack_types": ["Flood Attacks", "Reconnaissance"],
    "top_source_ips": ["192.168.100.200", "34.160.144.191"]
}

# Calcul du score de risque
risk_score = (threat_data["high_risk"] * 3 + threat_data["medium_risk"] * 2) / threat_data["total_threats"]

print(f"📊 Score de risque: {risk_score:.1f}/3.0")
print(f"🎯 Total menaces: {threat_data['total_threats']}")
print(f"🔴 Menaces critiques: {threat_data['high_risk']}")
print(f"🟡 Menaces moyennes: {threat_data['medium_risk']}")

# Recommandations
print("\\n🛡️ RECOMMANDATIONS:")
if risk_score > 2.5:
    print("- URGENT: Bloquer les IPs suspectes")
    print("- Activer la surveillance renforcée")
    print("- Notifier l'équipe de sécurité")
elif risk_score > 1.5:
    print("- Surveiller les patterns d'attaque")
    print("- Renforcer les règles de firewall")
else:
    print("- Surveillance normale")

print(f"\\n✅ Analyse terminée à {datetime.now().strftime('%H:%M:%S')}")`)
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Database className="w-8 h-8 text-blue-500" />
              Explorateur de Base de Données PostgreSQL
            </h1>
            <p className="text-muted-foreground mt-2">
              Interface complète pour explorer la base de données, exécuter SQL et Python
            </p>
          </div>
          <Button onClick={loadTables} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        </div>

        <Tabs defaultValue="tables" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="tables" className="flex items-center gap-2">
              <TableIcon className="w-4 h-4" />
              Tables
            </TabsTrigger>
            <TabsTrigger value="sql" className="flex items-center gap-2">
              <Terminal className="w-4 h-4" />
              SQL Query
            </TabsTrigger>
            <TabsTrigger value="python" className="flex items-center gap-2">
              <Code className="w-4 h-4" />
              Python Script
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Historique
            </TabsTrigger>
          </TabsList>

          {/* Tables Tab */}
          <TabsContent value="tables" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tables List */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TableIcon className="w-5 h-5" />
                    Tables PostgreSQL ({tables.length})
                  </CardTitle>
                  <CardDescription>
                    Cliquez sur une table pour voir ses détails
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {tables.map((table) => (
                      <div
                        key={table.tablename}
                        className={`p-3 border rounded-lg cursor-pointer hover:bg-muted transition-colors ${
                          selectedTable === table.tablename ? 'bg-muted border-primary' : ''
                        }`}
                        onClick={() => loadTableDetails(table.tablename)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{table.tablename}</h4>
                            <p className="text-sm text-muted-foreground">
                              {table.row_count} lignes • {table.size}
                            </p>
                          </div>
                          <div className="flex gap-1">
                            {table.hasindexes && <Badge variant="secondary">Index</Badge>}
                            {table.hasrules && <Badge variant="secondary">Rules</Badge>}
                            {table.hastriggers && <Badge variant="secondary">Triggers</Badge>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Table Details */}
              {selectedTable && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Eye className="w-5 h-5" />
                      Table: {selectedTable}
                    </CardTitle>
                    <CardDescription>
                      Structure et données de la table
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Columns */}
                    <div>
                      <h4 className="font-medium mb-2">Colonnes ({tableColumns.length})</h4>
                      <div className="space-y-1 max-h-40 overflow-y-auto">
                        {tableColumns.map((col) => (
                          <div key={col.column_name} className="flex items-center justify-between text-sm border-b pb-1">
                            <span className="font-mono">{col.column_name}</span>
                            <div className="flex gap-2">
                              <Badge variant="outline">{col.data_type}</Badge>
                              {col.is_nullable === 'NO' && <Badge variant="destructive" className="text-xs">NOT NULL</Badge>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Sample Data */}
                    <div>
                      <h4 className="font-medium mb-2">Données (50 premières lignes)</h4>
                      <div className="border rounded-lg overflow-auto max-h-60">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              {tableColumns.slice(0, 4).map((col) => (
                                <TableHead key={col.column_name} className="text-xs">
                                  {col.column_name}
                                </TableHead>
                              ))}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {tableData.slice(0, 10).map((row, idx) => (
                              <TableRow key={idx}>
                                {tableColumns.slice(0, 4).map((col) => (
                                  <TableCell key={col.column_name} className="text-xs max-w-32 truncate">
                                    {String(row[col.column_name] || '').substring(0, 50)}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* SQL Query Tab */}
          <TabsContent value="sql" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Terminal className="w-5 h-5" />
                    Requête SQL
                  </CardTitle>
                  <CardDescription>
                    Exécutez des requêtes SQL personnalisées
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button onClick={setSampleSqlQuery} variant="outline" size="sm">
                      Exemple SQL
                    </Button>
                  </div>
                  <Textarea
                    placeholder="Entrez votre requête SQL ici..."
                    value={sqlQuery}
                    onChange={(e) => setSqlQuery(e.target.value)}
                    className="min-h-40 font-mono text-sm"
                  />
                  <Button onClick={executeSqlQuery} disabled={sqlLoading || !sqlQuery.trim()}>
                    <Play className={`w-4 h-4 mr-2 ${sqlLoading ? 'animate-spin' : ''}`} />
                    Exécuter SQL
                  </Button>
                </CardContent>
              </Card>

              {/* SQL Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {sqlResult?.success ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : sqlResult?.success === false ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <FileText className="w-5 h-5" />
                    )}
                    Résultat SQL
                  </CardTitle>
                  {sqlResult && (
                    <CardDescription>
                      Temps d'exécution: {sqlResult.execution_time.toFixed(4)}s
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  {sqlResult ? (
                    <div className="space-y-4">
                      {sqlResult.success ? (
                        <div className="border rounded-lg overflow-auto max-h-80">
                          <pre className="p-4 text-sm">
                            {JSON.stringify(sqlResult.result, null, 2)}
                          </pre>
                        </div>
                      ) : (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <p className="text-red-700 text-sm">{sqlResult.error}</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">Aucun résultat pour le moment</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Python Script Tab */}
          <TabsContent value="python" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Script Python
                  </CardTitle>
                  <CardDescription>
                    Exécutez des scripts Python pour l'analyse de données
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button onClick={setSamplePythonScript} variant="outline" size="sm">
                      Exemple Python
                    </Button>
                  </div>
                  <Textarea
                    placeholder="Entrez votre code Python ici..."
                    value={pythonCode}
                    onChange={(e) => setPythonCode(e.target.value)}
                    className="min-h-40 font-mono text-sm"
                  />
                  <Button onClick={executePythonScript} disabled={pythonLoading || !pythonCode.trim()}>
                    <Play className={`w-4 h-4 mr-2 ${pythonLoading ? 'animate-spin' : ''}`} />
                    Exécuter Python
                  </Button>
                </CardContent>
              </Card>

              {/* Python Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {pythonResult?.success ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : pythonResult?.success === false ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <FileText className="w-5 h-5" />
                    )}
                    Résultat Python
                  </CardTitle>
                  {pythonResult && (
                    <CardDescription>
                      Temps d'exécution: {pythonResult.execution_time.toFixed(4)}s
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  {pythonResult ? (
                    <div className="space-y-4">
                      {pythonResult.success ? (
                        <div className="bg-gray-900 text-green-400 rounded-lg p-4 overflow-auto max-h-80">
                          <pre className="text-sm whitespace-pre-wrap">
                            {pythonResult.result}
                          </pre>
                        </div>
                      ) : (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <p className="text-red-700 text-sm">{pythonResult.error}</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">Aucun résultat pour le moment</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Historique des Requêtes
                </CardTitle>
                <CardDescription>
                  Historique des exécutions SQL et Python
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {queryHistory.map((entry) => (
                    <div key={entry.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={entry.query_type === 'SQL' ? 'default' : 'secondary'}>
                            {entry.query_type}
                          </Badge>
                          {entry.success ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-500" />
                          )}
                          <span className="text-sm text-muted-foreground">
                            {entry.execution_time.toFixed(4)}s
                          </span>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {new Date(entry.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="bg-muted rounded p-2">
                        <code className="text-sm">
                          {entry.query_text.substring(0, 200)}
                          {entry.query_text.length > 200 && '...'}
                        </code>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
