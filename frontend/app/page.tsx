"use client"

import { useState, useEffect } from "react";
import { apiClient } from "../lib/api";

import DashboardHome from '@/components/dashboard-home'
import MachineManagement from '@/components/machine-management'
import ThreatMonitoring from '@/components/threat-monitoring'
import LogManagement from '@/components/log-management'
import RuleManagement from '@/components/rule-management'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Shield,
  Lock,
  Eye,
  EyeOff,
  Menu,
  X,
  Home,
  Server,
  AlertTriangle,
  FileText,
  Settings,
  Activity,
  Users,
  Bell,
  Search,
  TrendingUp,
  Download,
  RefreshCw,
  Database,
  UserCheck,
  ShieldCheck,
  Plus,
  Edit,
  Trash2,
  Play,
  Pause,
  Copy,
  Upload,
  TestTube,
  BarChart3,
} from "lucide-react"
import {
  getAuditLogs,
  getSystemLogs,
  getSecurityLogs,
  getLogStatistics,
  exportLogs,
  getIDSRules,
  getRuleTemplates,
  getRuleStatistics,
  updateRule,
  deleteRule,
  testRule,
  exportRules,
  getBlockchainTransactions,
  getIntegrityReports,
  generateIntegrityReport,
  getBlockchainStatistics,
  verifyLogIntegrity,
  type AuditLog,
  type SystemLog,
  type SecurityLog,
  type IDSRule,
  type RuleTemplate,
  type BlockchainTransaction,
  type IntegrityReport,
} from "@/lib/database"

type NavigationItem = "dashboard" | "machines" | "threats" | "logs" | "rules" | "settings" | "blockchain"

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [credentials, setCredentials] = useState({
    username: "admin",
    password: "cyberguard2024",
  });
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const response = await apiClient.login(credentials.username, credentials.password);
      if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token);
        setIsAuthenticated(true);
      } else {
        setError("Login failed: No token received.");
      }
    } catch (err) {
      setError("Invalid credentials or server error. Please try again.");
      console.error("Login failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated) {
    return <Dashboard />;
  }

  return (
    <div className="min-h-screen bg-background cyber-grid flex items-center justify-center p-4">
      <Card className="w-full max-w-md glow-effect">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-3 bg-primary/20 rounded-full">
              <Shield className="h-8 w-8 text-primary" />
            </div>
          </div>
          <div>
            <CardTitle className="text-2xl font-bold">CyberGuard IDS/IPS</CardTitle>
            <CardDescription>Secure access to cybersecurity monitoring dashboard</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="p-3 mb-4 text-sm text-red-700 bg-red-100 rounded-lg dark:bg-red-200 dark:text-red-800" role="alert">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={credentials.username}
                onChange={(e) => setCredentials((prev) => ({ ...prev, username: e.target.value }))}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={(e) => setCredentials((prev) => ({ ...prev, password: e.target.value }))}
                  required
                  disabled={isLoading}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <Lock className="mr-2 h-4 w-4" />
                  Secure Login
                </>
              )}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm text-muted-foreground">Demo credentials: admin / cyberguard2024</div>
        </CardContent>
      </Card>
    </div>
  );
}

function Dashboard() {
  const [activeView, setActiveView] = useState<NavigationItem>("dashboard")

  const renderContent = () => {
    switch (activeView) {
      case "dashboard":
        return <DashboardHome />
      case "machines":
        return <MachineManagement />
      case "threats":
        return <ThreatMonitoring />
      case "logs":
        return <LogManagement />
      case "rules":
        return <RuleManagement />
      case "blockchain":
        return <BlockchainManagement />
      case "settings":
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold">Settings</h2>
            <p className="text-muted-foreground">Coming in next phase...</p>
          </div>
        )
      default:
        return <DashboardHome />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Content Area */}
      <main className="">{renderContent()}</main>
    </div>
  )
}

function LogManagement() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [systemLogs, setSystemLogs] = useState<SystemLog[]>([])
  const [securityLogs, setSecurityLogs] = useState<SecurityLog[]>([])
  const [filteredLogs, setFilteredLogs] = useState<any[]>([])
  const [activeLogType, setActiveLogType] = useState<"audit" | "system" | "security">("audit")
  const [searchTerm, setSearchTerm] = useState("")
  const [severityFilter, setSeverityFilter] = useState<string>("all")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [dateFilter, setDateFilter] = useState<string>("all")
  const [logStats, setLogStats] = useState<any>(null)
  const [selectedLog, setSelectedLog] = useState<any>(null)

  useEffect(() => {
    // Load logs and statistics
    Promise.all([getAuditLogs(), getSystemLogs(), getSecurityLogs(), getLogStatistics()]).then(
      ([audit, system, security, stats]) => {
        setAuditLogs(audit)
        setSystemLogs(system)
        setSecurityLogs(security)
        setLogStats(stats)
      },
    )
  }, [])

  useEffect(() => {
    let logs: any[] = []
    switch (activeLogType) {
      case "audit":
        logs = auditLogs
        break
      case "system":
        logs = systemLogs
        break
      case "security":
        logs = securityLogs
        break
    }

    let filtered = logs

    if (searchTerm) {
      filtered = filtered.filter(
        (log) =>
          log.details?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.message?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.component?.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    if (severityFilter !== "all") {
      filtered = filtered.filter((log) => log.severity === severityFilter || log.level === severityFilter)
    }

    if (categoryFilter !== "all") {
      filtered = filtered.filter(
        (log) =>
          log.category === categoryFilter || log.event_type === categoryFilter || log.component === categoryFilter,
      )
    }

    if (dateFilter !== "all") {
      const now = new Date()
      let cutoff: Date
      switch (dateFilter) {
        case "1h":
          cutoff = new Date(now.getTime() - 60 * 60 * 1000)
          break
        case "24h":
          cutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000)
          break
        case "7d":
          cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          break
        default:
          cutoff = new Date(0)
      }
      filtered = filtered.filter((log) => log.timestamp > cutoff)
    }

    setFilteredLogs(filtered)
  }, [auditLogs, systemLogs, securityLogs, activeLogType, searchTerm, severityFilter, categoryFilter, dateFilter])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "info":
      case "debug":
        return "default"
      case "warning":
        return "secondary"
      case "error":
        return "destructive"
      case "critical":
        return "destructive"
      default:
        return "default"
    }
  }

  const handleExport = async (format: "csv" | "json") => {
    const dateRange = {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
      end: new Date(),
    }
    const result = await exportLogs(activeLogType, format, dateRange)
    alert(`Export initiated: ${result.filename}`)
  }

  const chartData = logStats
    ? [
        {
          name: "Info",
          value: logStats[activeLogType]?.bySeverity?.info || logStats[activeLogType]?.byLevel?.info || 0,
          color: "#22c55e",
        },
        {
          name: "Warning",
          value: logStats[activeLogType]?.bySeverity?.warning || logStats[activeLogType]?.byLevel?.warning || 0,
          color: "#f59e0b",
        },
        {
          name: "Error",
          value: logStats[activeLogType]?.bySeverity?.error || logStats[activeLogType]?.byLevel?.error || 0,
          color: "#ef4444",
        },
        {
          name: "Critical",
          value: logStats[activeLogType]?.bySeverity?.critical || logStats[activeLogType]?.byLevel?.critical || 0,
          color: "#dc2626",
        },
      ]
    : []

  return (
    <div className="p-6 space-y-6">
      {/* Log Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className={activeLogType === "audit" ? "ring-2 ring-primary" : ""}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Audit Logs</p>
                <p className="text-2xl font-bold">{logStats?.audit?.total || 0}</p>
                <p className="text-xs text-muted-foreground">Last hour: {logStats?.audit?.lastHour || 0}</p>
              </div>
              <UserCheck className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className={activeLogType === "system" ? "ring-2 ring-primary" : ""}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">System Logs</p>
                <p className="text-2xl font-bold">{logStats?.system?.total || 0}</p>
                <p className="text-xs text-muted-foreground">Last hour: {logStats?.system?.lastHour || 0}</p>
              </div>
              <Database className="h-8 w-8 text-chart-2" />
            </div>
          </CardContent>
        </Card>

        <Card className={activeLogType === "security" ? "ring-2 ring-primary" : ""}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Security Logs</p>
                <p className="text-2xl font-bold">{logStats?.security?.total || 0}</p>
                <p className="text-xs text-muted-foreground">Last hour: {logStats?.security?.lastHour || 0}</p>
              </div>
              <ShieldCheck className="h-8 w-8 text-chart-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Risk Score</p>
                <p className="text-2xl font-bold">{Math.round(logStats?.security?.averageRiskScore || 0)}</p>
                <p className="text-xs text-muted-foreground">Security events</p>
              </div>
              <TrendingUp className="h-8 w-8 text-chart-4" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Log Type Tabs and Controls */}
      <Tabs value={activeLogType} onValueChange={(value) => setActiveLogType(value as any)} className="space-y-4">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="compliance">Compliance</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="ids">IDS/IPS</TabsTrigger>
            <TabsTrigger value="audit">Audit Logs</TabsTrigger>
            <TabsTrigger value="system">System Logs</TabsTrigger>
            <TabsTrigger value="security">Security Logs</TabsTrigger>
          </TabsList>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={() => handleExport("csv")}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport("json")}>
              <Download className="h-4 w-4 mr-2" />
              Export JSON
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search logs by message, user, action, or component..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
              <Select value={severityFilter} onValueChange={setSeverityFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="debug">Debug</SelectItem>
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {activeLogType === "audit" && (
                    <>
                      <SelectItem value="authentication">Authentication</SelectItem>
                      <SelectItem value="authorization">Authorization</SelectItem>
                      <SelectItem value="data_access">Data Access</SelectItem>
                      <SelectItem value="configuration">Configuration</SelectItem>
                      <SelectItem value="user_management">User Management</SelectItem>
                    </>
                  )}
                  {activeLogType === "system" && (
                    <>
                      <SelectItem value="database">Database</SelectItem>
                      <SelectItem value="network">Network</SelectItem>
                      <SelectItem value="application">Application</SelectItem>
                      <SelectItem value="security">Security</SelectItem>
                      <SelectItem value="performance">Performance</SelectItem>
                    </>
                  )}
                  {activeLogType === "security" && (
                    <>
                      <SelectItem value="intrusion_attempt">Intrusion Attempt</SelectItem>
                      <SelectItem value="malware_detection">Malware Detection</SelectItem>
                      <SelectItem value="policy_violation">Policy Violation</SelectItem>
                      <SelectItem value="anomaly_detection">Anomaly Detection</SelectItem>
                      <SelectItem value="threat_intelligence">Threat Intelligence</SelectItem>
                    </>
                  )}
                </SelectContent>
              </Select>
              <Select value={dateFilter} onValueChange={setDateFilter}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Time" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Time</SelectItem>
                  <SelectItem value="1h">Last Hour</SelectItem>
                  <SelectItem value="24h">Last 24h</SelectItem>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Log Display */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{activeLogType.charAt(0).toUpperCase() + activeLogType.slice(1)} Logs</span>
              <Badge variant="outline">{filteredLogs.length} entries</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredLogs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No logs found matching the current filters.
                </div>
              ) : (
                filteredLogs.map((log, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-4 p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => setSelectedLog(log)}
                  >
                    <div className="flex-shrink-0">
                      <Badge variant={getSeverityColor(log.severity || log.level)}>{log.severity || log.level}</Badge>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">{log.action || log.message || log.event_type}</p>
                        <p className="text-xs text-muted-foreground">{log.timestamp.toLocaleTimeString()}</p>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {activeLogType === "audit" && `User: ${log.username} | IP: ${log.ip_address}`}
                        {activeLogType === "system" && `Component: ${log.component} | ${log.details}`}
                        {activeLogType === "security" && `Source: ${log.source_ip} | Risk: ${log.risk_score}`}
                      </p>
                      {log.details && <p className="text-xs text-muted-foreground mt-1 truncate">{log.details}</p>}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </Tabs>

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Log Details</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setSelectedLog(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Timestamp</Label>
                  <p className="text-sm">{selectedLog.timestamp.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Severity</Label>
                  <Badge variant={getSeverityColor(selectedLog.severity || selectedLog.level)}>
                    {selectedLog.severity || selectedLog.level}
                  </Badge>
                </div>
                {selectedLog.username && (
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground">User</Label>
                    <p className="text-sm">{selectedLog.username}</p>
                  </div>
                )}
                {selectedLog.ip_address && (
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground">IP Address</Label>
                    <p className="text-sm">{selectedLog.ip_address}</p>
                  </div>
                )}
                {selectedLog.component && (
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground">Component</Label>
                    <p className="text-sm">{selectedLog.component}</p>
                  </div>
                )}
                {selectedLog.source_ip && (
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground">Source IP</Label>
                    <p className="text-sm">{selectedLog.source_ip}</p>
                  </div>
                )}
                {selectedLog.risk_score && (
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground">Risk Score</Label>
                    <p className="text-sm">{selectedLog.risk_score}</p>
                  </div>
                )}
              </div>
              <div>
                <Label className="text-xs font-medium text-muted-foreground">
                  {selectedLog.action ? "Action" : selectedLog.message ? "Message" : "Event Type"}
                </Label>
                <p className="text-sm mt-1">{selectedLog.action || selectedLog.message || selectedLog.event_type}</p>
              </div>
              {selectedLog.details && (
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Details</Label>
                  <p className="text-sm mt-1 whitespace-pre-wrap">{selectedLog.details}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function BlockchainManagement() {
  const [transactions, setTransactions] = useState<BlockchainTransaction[]>([])
  const [integrityReports, setIntegrityReports] = useState<IntegrityReport[]>([])
  const [blockchainStats, setBlockchainStats] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<"transactions" | "integrity" | "explorer" | "statistics">("transactions")
  const [selectedTransaction, setSelectedTransaction] = useState<BlockchainTransaction | null>(null)
  const [verificationResults, setVerificationResults] = useState<Record<string, boolean>>({})
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [logTypeFilter, setLogTypeFilter] = useState<string>("all")

  useEffect(() => {
    Promise.all([getBlockchainTransactions(), getIntegrityReports(), getBlockchainStatistics()]).then(
      ([txData, reportsData, statsData]) => {
        setTransactions(txData)
        setIntegrityReports(reportsData)
        setBlockchainStats(statsData)
      },
    )
  }, [])

  const handleVerifyLog = async (logId: string, logType: "audit" | "system" | "security") => {
    const isValid = await verifyLogIntegrity(logId, logType)
    setVerificationResults((prev) => ({ ...prev, [logId]: isValid }))
  }

  const handleGenerateReport = async (logType: "audit" | "system" | "security") => {
    const report = await generateIntegrityReport(logType)
    setIntegrityReports((prev) => [...prev.filter((r) => r.log_type !== logType), report])
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "default"
      case "pending":
        return "secondary"
      case "failed":
        return "destructive"
      default:
        return "outline"
    }
  }

  const getIntegrityColor = (score: number) => {
    if (score >= 95) return "default"
    if (score >= 80) return "secondary"
    if (score >= 60) return "destructive"
    return "destructive"
  }

  const filteredTransactions = transactions.filter((tx) => {
    const matchesSearch =
      tx.tx_hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.log_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || tx.status === statusFilter
    const matchesLogType = logTypeFilter === "all" || tx.log_type === logTypeFilter
    return matchesSearch && matchesStatus && matchesLogType
  })

  return (
    <div className="p-6 space-y-6">
      {/* Blockchain Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Transactions</p>
                <p className="text-2xl font-bold">{blockchainStats?.totalTransactions || 0}</p>
                <p className="text-xs text-muted-foreground">{blockchainStats?.confirmedTransactions || 0} confirmed</p>
              </div>
              <Database className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Integrity</p>
                <p className="text-2xl font-bold">
                  {blockchainStats?.overallIntegrity ? `${blockchainStats.overallIntegrity.toFixed(1)}%` : "0%"}
                </p>
                <p className="text-xs text-muted-foreground">Across all log types</p>
              </div>
              <ShieldCheck className="h-8 w-8 text-chart-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending Transactions</p>
                <p className="text-2xl font-bold">{blockchainStats?.pendingTransactions || 0}</p>
                <p className="text-xs text-muted-foreground">Awaiting confirmation</p>
              </div>
              <RefreshCw className="h-8 w-8 text-chart-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Gas Used</p>
                <p className="text-2xl font-bold">{blockchainStats?.totalGasUsed?.toLocaleString() || 0}</p>
                <p className="text-xs text-muted-foreground">Total network cost</p>
              </div>
              <TrendingUp className="h-8 w-8 text-chart-4" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="space-y-4">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="integrity">Integrity Reports</TabsTrigger>
            <TabsTrigger value="explorer">Block Explorer</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
          </TabsList>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={() => handleGenerateReport("audit")}>
              <BarChart3 className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {activeTab === "transactions" && (
          <>
            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search by transaction hash or log ID..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-8"
                      />
                    </div>
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="confirmed">Confirmed</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={logTypeFilter} onValueChange={setLogTypeFilter}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Log Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="audit">Audit</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                      <SelectItem value="security">Security</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Transactions List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Blockchain Transactions</span>
                  <Badge variant="outline">{filteredTransactions.length} transactions</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {filteredTransactions.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No transactions found matching the current filters.
                    </div>
                  ) : (
                    filteredTransactions.map((tx) => (
                      <div
                        key={tx.id}
                        className="flex items-center space-x-4 p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                        onClick={() => setSelectedTransaction(tx)}
                      >
                        <div className="flex-shrink-0">
                          <Badge variant={getStatusColor(tx.status)}>{tx.status}</Badge>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <p className="text-sm font-medium font-mono truncate">{tx.tx_hash}</p>
                              <Badge variant="outline">{tx.log_type}</Badge>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-muted-foreground">Block: {tx.block_number}</span>
                              <span className="text-xs text-muted-foreground">Confirmations: {tx.confirmations}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                            <span>Log ID: {tx.log_id}</span>
                            <span>Gas: {tx.gas_used.toLocaleString()}</span>
                            <span>Network: {tx.network}</span>
                            <span>{tx.timestamp.toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleVerifyLog(tx.log_id, tx.log_type)
                            }}
                          >
                            <ShieldCheck className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {activeTab === "integrity" && (
          <div className="space-y-6">
            {/* Integrity Overview */}
            <div className="grid gap-4 md:grid-cols-3">
              {integrityReports.map((report) => (
                <Card key={report.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="capitalize">{report.log_type} Logs</span>
                      <Badge variant={getIntegrityColor(report.integrity_score)}>
                        {report.integrity_score.toFixed(1)}%
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Total Logs</p>
                        <p className="font-medium">{report.total_logs}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Verified</p>
                        <p className="font-medium text-green-600">{report.verified_logs}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Tampered</p>
                        <p className="font-medium text-red-600">{report.tampered_logs}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Missing Hash</p>
                        <p className="font-medium text-yellow-600">{report.missing_hashes}</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs text-muted-foreground">Sync Status</p>
                        <Badge variant={report.blockchain_sync_status === "synced" ? "default" : "secondary"}>
                          {report.blockchain_sync_status}
                        </Badge>
                      </div>
                      <Button variant="outline" size="sm" onClick={() => handleGenerateReport(report.log_type)}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === "explorer" && (
          <Card>
            <CardHeader>
              <CardTitle>Blockchain Explorer</CardTitle>
              <CardDescription>Browse blocks and transactions on the private blockchain network</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center py-8 text-muted-foreground">
                  <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Block explorer functionality coming soon...</p>
                  <p className="text-sm">
                    View detailed block information, transaction history, and network statistics
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === "statistics" && (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Transaction Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Confirmed Transactions</span>
                    <Badge variant="default">{blockchainStats?.confirmedTransactions || 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Pending Transactions</span>
                    <Badge variant="secondary">{blockchainStats?.pendingTransactions || 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Failed Transactions</span>
                    <Badge variant="destructive">{blockchainStats?.failedTransactions || 0}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Average Confirmations</span>
                    <Badge variant="outline">{blockchainStats?.averageConfirmations?.toFixed(1) || 0}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Integrity Scores by Log Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Audit Logs</span>
                    <Badge variant={getIntegrityColor(blockchainStats?.integrityScores?.audit || 0)}>
                      {blockchainStats?.integrityScores?.audit?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>System Logs</span>
                    <Badge variant={getIntegrityColor(blockchainStats?.integrityScores?.system || 0)}>
                      {blockchainStats?.integrityScores?.system?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Security Logs</span>
                    <Badge variant={getIntegrityColor(blockchainStats?.integrityScores?.security || 0)}>
                      {blockchainStats?.integrityScores?.security?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="font-medium">Overall Integrity</span>
                    <Badge variant={getIntegrityColor(blockchainStats?.overallIntegrity || 0)}>
                      {blockchainStats?.overallIntegrity?.toFixed(1) || 0}%
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </Tabs>

      {/* Transaction Detail Modal */}
      {selectedTransaction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <span>Transaction Details</span>
                  <Badge variant={getStatusColor(selectedTransaction.status)}>{selectedTransaction.status}</Badge>
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setSelectedTransaction(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Transaction Hash</Label>
                  <p className="text-sm font-mono break-all">{selectedTransaction.tx_hash}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Block Number</Label>
                  <p className="text-sm">{selectedTransaction.block_number}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Log Type</Label>
                  <p className="text-sm capitalize">{selectedTransaction.log_type}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Log ID</Label>
                  <p className="text-sm">{selectedTransaction.log_id}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Gas Used</Label>
                  <p className="text-sm">{selectedTransaction.gas_used.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Confirmations</Label>
                  <p className="text-sm">{selectedTransaction.confirmations}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Network</Label>
                  <p className="text-sm capitalize">{selectedTransaction.network}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Timestamp</Label>
                  <p className="text-sm">{selectedTransaction.timestamp.toLocaleString()}</p>
                </div>
              </div>

              <div>
                <Label className="text-xs font-medium text-muted-foreground">Data Hash</Label>
                <div className="mt-1 p-3 bg-muted rounded-md">
                  <code className="text-sm font-mono break-all">{selectedTransaction.data_hash}</code>
                </div>
              </div>

              <div>
                <Label className="text-xs font-medium text-muted-foreground">Previous Hash</Label>
                <div className="mt-1 p-3 bg-muted rounded-md">
                  <code className="text-sm font-mono break-all">{selectedTransaction.previous_hash}</code>
                </div>
              </div>

              <div>
                <Label className="text-xs font-medium text-muted-foreground">Merkle Root</Label>
                <div className="mt-1 p-3 bg-muted rounded-md">
                  <code className="text-sm font-mono break-all">{selectedTransaction.merkle_root}</code>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  onClick={() => handleVerifyLog(selectedTransaction.log_id, selectedTransaction.log_type)}
                >
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  Verify Integrity
                </Button>
                {verificationResults[selectedTransaction.log_id] !== undefined && (
                  <Badge variant={verificationResults[selectedTransaction.log_id] ? "default" : "destructive"}>
                    {verificationResults[selectedTransaction.log_id] ? "Verified" : "Failed"}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
