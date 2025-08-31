"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Activity, Wifi, Server, Globe, RefreshCw, Eye } from 'lucide-react'

export default function NetworkMonitorPage() {
  const [interfaces, setInterfaces] = useState([
    {
      name: "wlp0s20f3",
      type: "WiFi",
      status: "Active",
      packetsCapture: 15420,
      bytesTransferred: "2.4 GB",
      threats: 1250,
      ip: "192.168.1.124"
    },
    {
      name: "vmnet1", 
      type: "Virtual",
      status: "Active",
      packetsCapture: 8750,
      bytesTransferred: "1.2 GB", 
      threats: 450,
      ip: "192.168.100.1"
    },
    {
      name: "vmnet8",
      type: "Virtual", 
      status: "Active",
      packetsCapture: 5230,
      bytesTransferred: "890 MB",
      threats: 320,
      ip: "192.168.8.1"
    },
    {
      name: "lo",
      type: "Loopback",
      status: "Active", 
      packetsCapture: 1250,
      bytesTransferred: "45 MB",
      threats: 0,
      ip: "127.0.0.1"
    }
  ])

  const [networkStats, setNetworkStats] = useState({
    totalPackets: 30650,
    totalBytes: "4.5 GB",
    activeConnections: 127,
    threatsDetected: 2020,
    uptime: "2d 14h 32m"
  })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Network Monitor</h1>
          <p className="text-muted-foreground">Real-time network interface monitoring and packet analysis</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
          <Badge variant="outline" className="text-green-500 border-green-500">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
            Monitoring Active
          </Badge>
        </div>
      </div>

      {/* Network Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Total Packets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{networkStats.totalPackets.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Captured today</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Server className="h-4 w-4" />
              Data Transfer
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{networkStats.totalBytes}</div>
            <p className="text-xs text-muted-foreground">Total processed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Connections
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{networkStats.activeConnections}</div>
            <p className="text-xs text-muted-foreground">Active now</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Threats
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{networkStats.threatsDetected}</div>
            <p className="text-xs text-muted-foreground">Detected today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Uptime
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{networkStats.uptime}</div>
            <p className="text-xs text-muted-foreground">System running</p>
          </CardContent>
        </Card>
      </div>

      {/* Network Interfaces */}
      <Card>
        <CardHeader>
          <CardTitle>Network Interfaces</CardTitle>
          <CardDescription>Monitoring status of all network interfaces</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {interfaces.map((iface, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Wifi className="h-5 w-5 text-blue-500" />
                    <div>
                      <div className="font-semibold">{iface.name}</div>
                      <div className="text-sm text-muted-foreground">{iface.ip}</div>
                    </div>
                  </div>
                  
                  <Badge variant="outline">{iface.type}</Badge>
                  <Badge variant={iface.status === 'Active' ? 'default' : 'secondary'}>
                    {iface.status}
                  </Badge>
                </div>

                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <div className="font-semibold">{iface.packetsCapture.toLocaleString()}</div>
                    <div className="text-muted-foreground">Packets</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold">{iface.bytesTransferred}</div>
                    <div className="text-muted-foreground">Bytes</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-red-500">{iface.threats}</div>
                    <div className="text-muted-foreground">Threats</div>
                  </div>
                  <Button size="sm" variant="outline">
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Real-time Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Real-time Activity</CardTitle>
          <CardDescription>Live network packet monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
              <span className="font-mono">192.168.1.45 → 192.168.1.124</span>
              <span>TCP:443 (HTTPS)</span>
              <Badge variant="outline">Normal</Badge>
              <span className="text-muted-foreground">14:55:32</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-red-50 rounded text-sm">
              <span className="font-mono">34.69.34.144 → 192.168.1.124</span>
              <span>TCP:80 (HTTP)</span>
              <Badge variant="destructive">Flood Attack</Badge>
              <span className="text-muted-foreground">14:55:31</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
              <span className="font-mono">192.168.1.124 → 8.8.8.8</span>
              <span>UDP:53 (DNS)</span>
              <Badge variant="outline">Normal</Badge>
              <span className="text-muted-foreground">14:55:30</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
