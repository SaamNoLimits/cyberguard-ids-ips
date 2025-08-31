"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Users, UserPlus, Shield, Settings, Eye, Edit } from 'lucide-react'

export default function UsersPage() {
  const users = [
    {
      id: "1",
      name: "Admin User",
      email: "admin@cyberguard.com",
      role: "Administrator",
      status: "Active",
      lastLogin: "2025-08-28 14:30:00",
      permissions: ["Full Access", "User Management", "System Config"]
    },
    {
      id: "2", 
      name: "Security Analyst",
      email: "analyst@cyberguard.com",
      role: "Analyst",
      status: "Active",
      lastLogin: "2025-08-28 13:45:00",
      permissions: ["Threat Monitoring", "Reports", "Database Read"]
    },
    {
      id: "3",
      name: "Network Engineer", 
      email: "network@cyberguard.com",
      role: "Engineer",
      status: "Active",
      lastLogin: "2025-08-28 12:15:00",
      permissions: ["Network Monitor", "Configuration", "Reports"]
    },
    {
      id: "4",
      name: "Guest User",
      email: "guest@cyberguard.com", 
      role: "Viewer",
      status: "Inactive",
      lastLogin: "2025-08-25 09:30:00",
      permissions: ["Dashboard View", "Reports Read"]
    }
  ]

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Administrator': return 'bg-red-500 text-white'
      case 'Analyst': return 'bg-blue-500 text-white'
      case 'Engineer': return 'bg-green-500 text-white'
      case 'Viewer': return 'bg-gray-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const getStatusColor = (status: string) => {
    return status === 'Active' ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground">Manage system users, roles, and permissions</p>
        </div>
        <Button>
          <UserPlus className="h-4 w-4 mr-2" />
          Add New User
        </Button>
      </div>

      {/* User Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{users.length}</div>
            <p className="text-xs text-muted-foreground">Registered users</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {users.filter(u => u.status === 'Active').length}
            </div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Administrators
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {users.filter(u => u.role === 'Administrator').length}
            </div>
            <p className="text-xs text-muted-foreground">Admin privileges</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Online Now
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">2</div>
            <p className="text-xs text-muted-foreground">Currently online</p>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>System Users</CardTitle>
          <CardDescription>Manage user accounts, roles, and permissions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-muted-foreground">{user.email}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getRoleColor(user.role)}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(user.status)}>
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {user.lastLogin}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {user.permissions.slice(0, 2).map((perm, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                        {user.permissions.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{user.permissions.length - 2} more
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Role Permissions */}
      <Card>
        <CardHeader>
          <CardTitle>Role Permissions Matrix</CardTitle>
          <CardDescription>Overview of permissions by user role</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-red-500 mb-2">Administrator</h3>
              <ul className="text-sm space-y-1">
                <li>✓ Full System Access</li>
                <li>✓ User Management</li>
                <li>✓ System Configuration</li>
                <li>✓ All Modules</li>
              </ul>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-blue-500 mb-2">Analyst</h3>
              <ul className="text-sm space-y-1">
                <li>✓ Threat Monitoring</li>
                <li>✓ Database Access</li>
                <li>✓ Report Generation</li>
                <li>✗ User Management</li>
              </ul>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-green-500 mb-2">Engineer</h3>
              <ul className="text-sm space-y-1">
                <li>✓ Network Monitor</li>
                <li>✓ Configuration</li>
                <li>✓ Reports</li>
                <li>✗ User Management</li>
              </ul>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-500 mb-2">Viewer</h3>
              <ul className="text-sm space-y-1">
                <li>✓ Dashboard View</li>
                <li>✓ Reports Read</li>
                <li>✗ Data Modification</li>
                <li>✗ Configuration</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
