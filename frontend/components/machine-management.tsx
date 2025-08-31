"use client"

import React, { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { RefreshCw, Server, AlertCircle } from 'lucide-react'

interface VirtualMachine {
  id: string
  name: string
  ip_address: string
  os: string
  status: 'running' | 'stopped' | 'error'
  threat_level: 'low' | 'medium' | 'high' | 'critical'
  last_seen: string
}

export default function MachineManagement() {
  const [machines, setMachines] = useState<VirtualMachine[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMachines()
  }, [])

  const loadMachines = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await apiClient.getMachines()
      setMachines(data)
    } catch (err) {
      setError('Failed to fetch machine data. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-500 text-white">Running</Badge>
      case 'stopped':
        return <Badge variant="secondary">Stopped</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  const getThreatLevelBadge = (level: string) => {
    switch (level) {
      case 'low':
        return <Badge className="bg-blue-500 text-white">Low</Badge>
      case 'medium':
        return <Badge className="bg-yellow-500 text-white">Medium</Badge>
      case 'high':
        return <Badge className="bg-orange-500 text-white">High</Badge>
      case 'critical':
        return <Badge variant="destructive">Critical</Badge>
      default:
        return <Badge>{level}</Badge>
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Machine Management</h1>
          <p className="text-muted-foreground">Monitor and manage network devices and virtual machines</p>
        </div>
        <button onClick={loadMachines} disabled={isLoading} className="p-2 rounded-md hover:bg-muted">
          <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" /> {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Registered Machines</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="h-8 w-8 animate-spin" />
              <span className="ml-2">Loading machines...</span>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>OS</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Threat Level</TableHead>
                  <TableHead>Last Seen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {machines.map((machine) => (
                  <TableRow key={machine.id}>
                    <TableCell className="font-medium flex items-center">
                      <Server className="h-4 w-4 mr-2 text-muted-foreground" />
                      {machine.name}
                    </TableCell>
                    <TableCell>{machine.ip_address}</TableCell>
                    <TableCell>{machine.os}</TableCell>
                    <TableCell>{getStatusBadge(machine.status)}</TableCell>
                    <TableCell>{getThreatLevelBadge(machine.threat_level)}</TableCell>
                    <TableCell>{new Date(machine.last_seen).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
