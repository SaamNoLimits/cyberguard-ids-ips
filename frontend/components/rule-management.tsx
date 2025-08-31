"use client"

import React, { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Activity, AlertTriangle, BarChart3, TrendingUp, Plus, Download, Upload, RefreshCw, Search, Pause, Play, Edit, TestTube, Trash2, Copy, X } from 'lucide-react'

// Interfaces (assuming these definitions)
interface IDSRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  pattern: string;
  action: 'alert' | 'block' | 'log' | 'quarantine' | 'redirect';
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  rule_type: string;
  performance_impact: 'low' | 'medium' | 'high';
  trigger_count: number;
  false_positive_rate: number;
  target_protocols: string[];
  target_ports: string[];
  conditions?: any;
  created_at: Date;
  updated_at: Date;
  created_by: string;
  last_triggered: Date | null;
}

interface RuleTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
}

export default function RuleManagement() {
  const [rules, setRules] = useState<IDSRule[]>([])
  const [templates, setTemplates] = useState<RuleTemplate[]>([])
  const [filteredRules, setFilteredRules] = useState<IDSRule[]>([])
  const [ruleStats, setRuleStats] = useState<any>(null)
  const [selectedRule, setSelectedRule] = useState<IDSRule | null>(null)
  const [editingRule, setEditingRule] = useState<IDSRule | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showTestDialog, setShowTestDialog] = useState(false)
  const [testResults, setTestResults] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [priorityFilter, setPriorityFilter] = useState<string>("all")
  const [activeTab, setActiveTab] = useState<"rules" | "templates" | "statistics">("rules")

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [rulesData, templatesData, statsData] = await Promise.all([
        apiClient.getRules(),
        apiClient.getRuleTemplates(),
        apiClient.getRuleStatistics(),
      ])
      setRules(rulesData.map((r: any) => ({ ...r, created_at: new Date(r.created_at), updated_at: new Date(r.updated_at), last_triggered: r.last_triggered ? new Date(r.last_triggered) : null })))
      setTemplates(templatesData)
      setRuleStats(statsData)
    } catch (error) {
      console.error("Failed to load rule data:", error)
    }
  }

  useEffect(() => {
    let filtered = rules

    if (searchTerm) {
      filtered = filtered.filter(
        (rule) =>
          rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          rule.pattern.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    if (categoryFilter !== "all") {
      filtered = filtered.filter((rule) => rule.category === categoryFilter)
    }

    if (statusFilter !== "all") {
      filtered = filtered.filter((rule) => (statusFilter === "enabled" ? rule.enabled : !rule.enabled))
    }

    if (priorityFilter !== "all") {
      filtered = filtered.filter((rule) => rule.priority === priorityFilter)
    }

    setFilteredRules(filtered)
  }, [rules, searchTerm, categoryFilter, statusFilter, priorityFilter])

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "low": return "default"
      case "medium": return "secondary"
      case "high": return "destructive"
      case "critical": return "destructive"
      default: return "default"
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case "alert": return "default"
      case "block": return "destructive"
      case "log": return "secondary"
      case "quarantine": return "destructive"
      case "redirect": return "secondary"
      default: return "default"
    }
  }

  const handleToggleRule = async (rule: IDSRule) => {
    try {
      const updated = await apiClient.updateRule(rule.id, { enabled: !rule.enabled })
      setRules(rules.map((r) => (r.id === rule.id ? { ...updated, created_at: new Date(updated.created_at), updated_at: new Date(updated.updated_at), last_triggered: updated.last_triggered ? new Date(updated.last_triggered) : null } : r)))
    } catch (error) {
      console.error("Failed to toggle rule status:", error)
    }
  }

  const handleDeleteRule = async (ruleId: string) => {
    if (confirm("Are you sure you want to delete this rule?")) {
      try {
        await apiClient.deleteRule(ruleId)
        setRules(rules.filter((r) => r.id !== ruleId))
        setSelectedRule(null)
      } catch (error) {
        console.error("Failed to delete rule:", error)
      }
    }
  }

  const handleTestRule = async (rule: IDSRule, testData: string) => {
    try {
      const results = await apiClient.testRule(rule.id, testData)
      setTestResults(results)
    } catch (error) {
      console.error("Failed to test rule:", error)
    }
  }

  const handleExportRules = async (format: "json" | "xml" | "yaml") => {
    try {
      const result = await apiClient.exportRules(format)
      alert(`Export completed: ${result.filename} (${result.count} rules)`)
    } catch (error) {
      console.error("Failed to export rules:", error)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Rule Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Rules</p>
                <p className="text-2xl font-bold">{ruleStats?.total || 0}</p>
                <p className="text-xs text-muted-foreground">
                  {ruleStats?.enabled || 0} enabled, {ruleStats?.disabled || 0} disabled
                </p>
              </div>
              <Activity className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Recent Triggers</p>
                <p className="text-2xl font-bold">{ruleStats?.recentlyTriggered || 0}</p>
                <p className="text-xs text-muted-foreground">Last hour</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-chart-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">False Positive Rate</p>
                <p className="text-2xl font-bold">
                  {ruleStats?.averageFalsePositiveRate
                    ? `${(ruleStats.averageFalsePositiveRate * 100).toFixed(1)}%`
                    : "0%"}
                </p>
                <p className="text-xs text-muted-foreground">Average across all rules</p>
              </div>
              <BarChart3 className="h-8 w-8 text-chart-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Triggers</p>
                <p className="text-2xl font-bold">{ruleStats?.totalTriggers || 0}</p>
                <p className="text-xs text-muted-foreground">All time</p>
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
            <TabsTrigger value="rules">Rules Management</TabsTrigger>
            <TabsTrigger value="templates">Rule Templates</TabsTrigger>
            <TabsTrigger value="statistics">Performance Stats</TabsTrigger>
          </TabsList>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={() => setShowCreateDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Rule
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExportRules("json")}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <Button variant="outline" size="sm" onClick={loadData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {activeTab === "rules" && (
          <>
            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search rules by name, description, or pattern..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-8"
                      />
                    </div>
                  </div>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="signature">Signature</SelectItem>
                      <SelectItem value="anomaly">Anomaly</SelectItem>
                      <SelectItem value="behavioral">Behavioral</SelectItem>
                      <SelectItem value="statistical">Statistical</SelectItem>
                      <SelectItem value="protocol">Protocol</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="enabled">Enabled</SelectItem>
                      <SelectItem value="disabled">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priority</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Rules List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>IDS/IPS Rules</span>
                  <Badge variant="outline">{filteredRules.length} rules</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {filteredRules.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No rules found matching the current filters.
                    </div>
                  ) : (
                    filteredRules.map((rule) => (
                      <div
                        key={rule.id}
                        className="flex items-center space-x-4 p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                        onClick={() => setSelectedRule(rule)}
                      >
                        <div className="flex-shrink-0">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleToggleRule(rule)
                            }}
                          >
                            {rule.enabled ? (
                              <Pause className="h-4 w-4 text-green-500" />
                            ) : (
                              <Play className="h-4 w-4 text-muted-foreground" />
                            )}
                          </Button>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <p className="text-sm font-medium truncate">{rule.name}</p>
                              <Badge variant={getPriorityColor(rule.priority)}>{rule.priority}</Badge>
                              <Badge variant={getActionColor(rule.action)}>{rule.action}</Badge>
                              <Badge variant="outline">{rule.category}</Badge>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-muted-foreground">Triggers: {rule.trigger_count}</span>
                              {rule.last_triggered && (
                                <span className="text-xs text-muted-foreground">
                                  Last: {rule.last_triggered.toLocaleTimeString()}
                                </span>
                              )}
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 truncate">{rule.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                            <span>FP Rate: {(rule.false_positive_rate * 100).toFixed(1)}%</span>
                            <span>Impact: {rule.performance_impact}</span>
                            <span>Protocols: {rule.target_protocols.join(", ")}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              setEditingRule(rule)
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedRule(rule)
                              setShowTestDialog(true)
                            }}
                          >
                            <TestTube className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteRule(rule.id)
                            }}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
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

        {activeTab === "templates" && (
          <Card>
            <CardHeader>
              <CardTitle>Rule Templates</CardTitle>
              <CardDescription>Pre-configured rule templates for common security scenarios</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates.map((template) => (
                  <div key={template.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{template.name}</h4>
                        <p className="text-sm text-muted-foreground">{template.description}</p>
                        <Badge variant="outline" className="mt-2">
                          {template.category}
                        </Badge>
                      </div>
                      <Button variant="outline" size="sm">
                        <Copy className="h-4 w-4 mr-2" />
                        Use Template
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === "statistics" && (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Rules by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {ruleStats &&
                    Object.entries(ruleStats.byCategory).map(([category, count]) => (
                      <div key={category} className="flex items-center justify-between">
                        <span className="capitalize">{category}</span>
                        <Badge variant="outline">{count as number}</Badge>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Impact</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {ruleStats &&
                    Object.entries(ruleStats.performanceImpact).map(([impact, count]) => (
                      <div key={impact} className="flex items-center justify-between">
                        <span className="capitalize">{impact}</span>
                        <Badge variant="outline">{count as number}</Badge>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </Tabs>

      {/* Rule Detail Modal */}
      {selectedRule && !showTestDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <span>{selectedRule.name}</span>
                  <Badge variant={getPriorityColor(selectedRule.priority)}>{selectedRule.priority}</Badge>
                  <Badge variant={getActionColor(selectedRule.action)}>{selectedRule.action}</Badge>
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setSelectedRule(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Category</Label>
                  <p className="text-sm capitalize">{selectedRule.category}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Rule Type</Label>
                  <p className="text-sm capitalize">{selectedRule.rule_type}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Status</Label>
                  <p className="text-sm">{selectedRule.enabled ? "Enabled" : "Disabled"}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Performance Impact</Label>
                  <p className="text-sm capitalize">{selectedRule.performance_impact}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Trigger Count</Label>
                  <p className="text-sm">{selectedRule.trigger_count}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">False Positive Rate</Label>
                  <p className="text-sm">{(selectedRule.false_positive_rate * 100).toFixed(1)}%</p>
                </div>
              </div>

              <div>
                <Label className="text-xs font-medium text-muted-foreground">Description</Label>
                <p className="text-sm mt-1">{selectedRule.description}</p>
              </div>

              <div>
                <Label className="text-xs font-medium text-muted-foreground">Pattern</Label>
                <div className="mt-1 p-3 bg-muted rounded-md">
                  <code className="text-sm font-mono">{selectedRule.pattern}</code>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Target Protocols</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedRule.target_protocols.map((protocol) => (
                      <Badge key={protocol} variant="outline" className="text-xs">
                        {protocol}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Target Ports</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedRule.target_ports.map((port) => (
                      <Badge key={port} variant="outline" className="text-xs">
                        {port}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {selectedRule.conditions && (
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Conditions</Label>
                  <div className="mt-1 p-3 bg-muted rounded-md">
                    <pre className="text-sm">{JSON.stringify(selectedRule.conditions, null, 2)}</pre>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Created</Label>
                  <p>{selectedRule.created_at.toLocaleDateString()}</p>
                  <p>by {selectedRule.created_by}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Last Updated</Label>
                  <p>{selectedRule.updated_at.toLocaleDateString()}</p>
                </div>
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Last Triggered</Label>
                  <p>{selectedRule.last_triggered ? selectedRule.last_triggered.toLocaleString() : "Never"}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Test Rule Modal */}
      {showTestDialog && selectedRule && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Test Rule: {selectedRule.name}</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowTestDialog(false)
                    setTestResults(null)
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="testData">Test Data</Label>
                <textarea
                  id="testData"
                  className="w-full h-32 p-3 border rounded-md resize-none"
                  placeholder="Enter test data to match against the rule pattern..."
                />
              </div>
              <Button
                onClick={() => {
                  const testData = (document.getElementById("testData") as HTMLTextAreaElement).value
                  handleTestRule(selectedRule, testData)
                }}
              >
                <TestTube className="h-4 w-4 mr-2" />
                Run Test
              </Button>

              {testResults && (
                <div className="mt-4 p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">Test Results</h4>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={testResults.matches ? "default" : "secondary"}>
                        {testResults.matches ? "Match" : "No Match"}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Processing time: {testResults.performance}ms
                      </span>
                    </div>
                    <p className="text-sm">{testResults.details}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
