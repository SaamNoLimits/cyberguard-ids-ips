"use client"

import React, { useState, useEffect, useMemo } from 'react'
import { apiClient } from '@/lib/api'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RefreshCw, Search, Download, FileText, Shield, Server } from 'lucide-react'

// Define interfaces for different log types
interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  details: string;
  status: 'success' | 'failure';
}

interface SystemLog {
  id: string;
  timestamp: string;
  service: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
}

interface SecurityLog {
  id: string;
  timestamp: string;
  source_ip: string;
  event_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

type LogType = 'audit' | 'system' | 'security';

export default function LogManagement() {
  const [logs, setLogs] = useState<any[]>([])
  const [logType, setLogType] = useState<LogType>('security')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadLogs()
  }, [logType])

  const loadLogs = async () => {
    try {
      setIsLoading(true)
      setError(null)
      let data;
      switch (logType) {
        case 'audit':
          data = await apiClient.getAuditLogs()
          break
        case 'system':
          data = await apiClient.getSystemLogs()
          break
        case 'security':
          data = await apiClient.getSecurityLogs()
          break
      }
      setLogs(data)
    } catch (err) {
      setError(`Failed to fetch ${logType} logs. Please try again.`)
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredLogs = useMemo(() => {
    return logs.filter(log =>
      Object.values(log).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
  }, [logs, searchTerm])

  const renderLogTable = () => {
    if (isLoading) return <div className="text-center p-8">Loading logs...</div>
    if (error) return <div className="text-center p-8 text-red-500">{error}</div>

    const headers = {
      audit: ['Timestamp', 'User', 'Action', 'Status'],
      system: ['Timestamp', 'Service', 'Level', 'Message'],
      security: ['Timestamp', 'Source IP', 'Event Type', 'Severity'],
    }

    const renderRow = (log: any) => {
      switch (logType) {
        case 'audit':
          return (
            <TableRow key={log.id}>
              <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
              <TableCell>{log.user}</TableCell>
              <TableCell>{log.action}</TableCell>
              <TableCell><Badge variant={log.status === 'success' ? 'default' : 'destructive'}>{log.status}</Badge></TableCell>
            </TableRow>
          )
        case 'system':
          return (
            <TableRow key={log.id}>
              <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
              <TableCell>{log.service}</TableCell>
              <TableCell>{log.level}</TableCell>
              <TableCell>{log.message}</TableCell>
            </TableRow>
          )
        case 'security':
          return (
            <TableRow key={log.id}>
              <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
              <TableCell>{log.source_ip}</TableCell>
              <TableCell>{log.event_type}</TableCell>
              <TableCell>{log.severity}</TableCell>
            </TableRow>
          )
      }
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            {headers[logType].map(h => <TableHead key={h}>{h}</TableHead>)}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredLogs.map(renderRow)}
        </TableBody>
      </Table>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Log Management</h1>
      <Tabs value={logType} onValueChange={(value) => setLogType(value as LogType)}>
        <TabsList>
          <TabsTrigger value="security"><Shield className="h-4 w-4 mr-2" />Security</TabsTrigger>
          <TabsTrigger value="system"><Server className="h-4 w-4 mr-2" />System</TabsTrigger>
          <TabsTrigger value="audit"><FileText className="h-4 w-4 mr-2" />Audit</TabsTrigger>
        </TabsList>
        <Card className="mt-4">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>{logType.charAt(0).toUpperCase() + logType.slice(1)} Logs</CardTitle>
                <CardDescription>Review and analyze system events.</CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Input 
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="outline" size="sm" onClick={loadLogs} disabled={isLoading}>
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
                <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" />Export</Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {renderLogTable()}
          </CardContent>
        </Card>
      </Tabs>
    </div>
  )
}
