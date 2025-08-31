"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Settings, Database, Shield, Network, Bell, Save } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">System Settings</h1>
          <p className="text-muted-foreground">Configure system parameters and security settings</p>
        </div>
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save All Changes
        </Button>
      </div>

      {/* Database Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database Configuration
          </CardTitle>
          <CardDescription>PostgreSQL database connection and storage settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Database Host</label>
              <Input defaultValue="localhost" />
            </div>
            <div>
              <label className="text-sm font-medium">Database Port</label>
              <Input defaultValue="5432" />
            </div>
            <div>
              <label className="text-sm font-medium">Database Name</label>
              <Input defaultValue="cybersec_ids" />
            </div>
            <div>
              <label className="text-sm font-medium">Username</label>
              <Input defaultValue="cybersec" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-green-500 border-green-500">
              Connected
            </Badge>
            <span className="text-sm text-muted-foreground">Database connection active</span>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security Configuration
          </CardTitle>
          <CardDescription>Threat detection and response settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Threat Confidence Threshold</label>
              <Input defaultValue="0.7" />
            </div>
            <div>
              <label className="text-sm font-medium">Auto-Block Threats</label>
              <select className="w-full p-2 border rounded-md">
                <option value="false">Manual Review</option>
                <option value="true">Automatic</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">PCAP Retention (days)</label>
              <Input defaultValue="30" />
            </div>
            <div>
              <label className="text-sm font-medium">Alert Frequency</label>
              <select className="w-full p-2 border rounded-md">
                <option value="realtime">Real-time</option>
                <option value="5min">Every 5 minutes</option>
                <option value="hourly">Hourly</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Network Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            Network Monitoring
          </CardTitle>
          <CardDescription>Network interface and packet capture settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Primary Interface</label>
              <select className="w-full p-2 border rounded-md">
                <option value="wlp0s20f3">wlp0s20f3 (WiFi)</option>
                <option value="vmnet1">vmnet1 (Virtual)</option>
                <option value="vmnet8">vmnet8 (Virtual)</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Packet Buffer Size</label>
              <Input defaultValue="1000" />
            </div>
            <div>
              <label className="text-sm font-medium">Capture Filter</label>
              <Input defaultValue="tcp or udp" />
            </div>
            <div>
              <label className="text-sm font-medium">Max Packet Size</label>
              <Input defaultValue="65535" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notifications
          </CardTitle>
          <CardDescription>Alert and notification preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">Email Alerts</div>
                <div className="text-sm text-muted-foreground">Send email notifications for critical threats</div>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">WebSocket Alerts</div>
                <div className="text-sm text-muted-foreground">Real-time browser notifications</div>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">SMS Alerts</div>
                <div className="text-sm text-muted-foreground">SMS notifications for high-priority threats</div>
              </div>
              <input type="checkbox" className="w-4 h-4" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>Current system health and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-500">Online</div>
              <div className="text-sm text-muted-foreground">System Status</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-blue-500">2d 14h</div>
              <div className="text-sm text-muted-foreground">Uptime</div>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-orange-500">15%</div>
              <div className="text-sm text-muted-foreground">CPU Usage</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
