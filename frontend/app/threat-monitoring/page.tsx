'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Clock, 
  Search,
  Filter,
  RefreshCw,
  Eye,
  Ban,
  ChevronLeft,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
interface Threat {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  attack_type: string;
  threat_level: string;
  confidence: number;
  description: string;
  blocked: boolean;
}

interface ThreatResponse {
  threats: Threat[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export default function ThreatMonitoringPage() {
  const router = useRouter();
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [attackTypeFilter, setAttackTypeFilter] = useState<string>('');
  const [threatLevelFilter, setThreatLevelFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalThreats, setTotalThreats] = useState(0);
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  const threatsPerPage = 20;

  const fetchThreats = useCallback(async (page: number = 1, search: string = '', attackType: string = '', threatLevel: string = '') => {
    try {
      setLoading(true);
      const offset = (page - 1) * threatsPerPage;
      
      const params = new URLSearchParams({
        limit: threatsPerPage.toString(),
        offset: offset.toString(),
        ...(search && { search }),
        ...(attackType && { attack_type: attackType }),
        ...(threatLevel && { threat_level: threatLevel })
      });

      const response = await fetch(`http://localhost:8000/api/public/threats/recent?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch threats');
      }
      
      const data = await response.json();
      // L'API retourne directement un tableau de menaces
      if (Array.isArray(data)) {
        setThreats(data);
        setTotalThreats(data.length);
      } else {
        // Si c'est un objet avec une propriété threats
        setThreats(data.threats || []);
        setTotalThreats(data.total || 0);
      }
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load threats');
    } finally {
      setLoading(false);
    }
  }, [threatsPerPage]);

  // Initial load and real-time updates
  useEffect(() => {
    fetchThreats(currentPage, searchTerm, attackTypeFilter, threatLevelFilter);
    
    let interval: NodeJS.Timeout;
    if (isRealTimeEnabled) {
      interval = setInterval(() => {
        fetchThreats(currentPage, searchTerm, attackTypeFilter, threatLevelFilter);
      }, 5000); // Update every 5 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentPage, searchTerm, attackTypeFilter, threatLevelFilter, isRealTimeEnabled, fetchThreats]);

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleAttackTypeFilter = (value: string) => {
    setAttackTypeFilter(value === 'all' ? '' : value);
    setCurrentPage(1);
  };

  const handleThreatLevelFilter = (value: string) => {
    setThreatLevelFilter(value === 'all' ? '' : value);
    setCurrentPage(1);
  };

  const getThreatLevelColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return 'bg-red-500';
      case 'HIGH': return 'bg-orange-500';
      case 'MEDIUM': return 'bg-yellow-500';
      case 'LOW': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getAttackTypeColor = (type: string) => {
    if (type.includes('Flood')) return 'bg-red-100 text-red-800';
    if (type.includes('Injection')) return 'bg-purple-100 text-purple-800';
    if (type.includes('Reconnaissance')) return 'bg-blue-100 text-blue-800';
    if (type.includes('Botnet')) return 'bg-orange-100 text-orange-800';
    if (type.includes('Spoofing')) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const totalPages = Math.ceil(totalThreats / threatsPerPage);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Threat Monitoring</h1>
              <p className="text-gray-600 mt-1">
                Real-time cybersecurity threat detection and analysis
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Badge variant={isRealTimeEnabled ? "default" : "secondary"} className="px-3 py-1">
                <Activity className={`w-3 h-3 mr-1 ${isRealTimeEnabled ? 'animate-pulse' : ''}`} />
                {isRealTimeEnabled ? 'Live' : 'Paused'}
              </Badge>
              <Button
                onClick={() => setIsRealTimeEnabled(!isRealTimeEnabled)}
                variant="outline"
                size="sm"
              >
                {isRealTimeEnabled ? 'Pause' : 'Resume'}
              </Button>
              <Button
                onClick={() => fetchThreats(currentPage, searchTerm, attackTypeFilter, threatLevelFilter)}
                variant="outline"
                size="sm"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Threats</p>
                    <p className="text-2xl font-bold">{totalThreats}</p>
                  </div>
                  <Shield className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Critical Threats</p>
                    <p className="text-2xl font-bold text-red-600">
                      {threats?.filter(t => t.threat_level === 'CRITICAL').length || 0}
                    </p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Blocked</p>
                    <p className="text-2xl font-bold text-green-600">
                      {threats?.filter(t => t.blocked).length || 0}
                    </p>
                  </div>
                  <Ban className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Last Update</p>
                    <p className="text-sm font-medium">
                      {lastUpdate.toLocaleTimeString()}
                    </p>
                  </div>
                  <Clock className="w-8 h-8 text-gray-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search threats by IP, description, or attack type..."
                      value={searchTerm}
                      onChange={(e) => handleSearch(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <Select value={attackTypeFilter || 'all'} onValueChange={handleAttackTypeFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Attack Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Attack Types</SelectItem>
                    <SelectItem value="Flood Attacks">Flood Attacks</SelectItem>
                    <SelectItem value="Injection Attacks">Injection Attacks</SelectItem>
                    <SelectItem value="Reconnaissance">Reconnaissance</SelectItem>
                    <SelectItem value="Botnet/Mirai Attacks">Botnet/Mirai</SelectItem>
                    <SelectItem value="Spoofing / MITM">Spoofing/MITM</SelectItem>
                    <SelectItem value="Backdoors & Exploits">Backdoors</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={threatLevelFilter || 'all'} onValueChange={handleThreatLevelFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Threat Level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Levels</SelectItem>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="MEDIUM">Medium</SelectItem>
                    <SelectItem value="LOW">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Threats Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Recent Threats ({totalThreats})</span>
              <Badge variant="outline">
                Page {currentPage} of {totalPages}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-16 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 font-medium">{error}</p>
                <Button 
                  onClick={() => fetchThreats(currentPage, searchTerm, attackTypeFilter, threatLevelFilter)}
                  className="mt-4"
                >
                  Try Again
                </Button>
              </div>
            ) : (threats?.length || 0) === 0 ? (
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No threats found matching your criteria</p>
              </div>
            ) : (
              <div className="space-y-2">
                {threats?.map((threat) => (
                  <div
                    key={threat.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => router.push(`/threat-details/${threat.id}`)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <Badge className={getThreatLevelColor(threat.threat_level)}>
                            {threat.threat_level}
                          </Badge>
                          <Badge variant="outline" className={getAttackTypeColor(threat.attack_type)}>
                            {threat.attack_type}
                          </Badge>
                          {threat.blocked && (
                            <Badge variant="destructive" className="text-xs">
                              <Ban className="w-3 h-3 mr-1" />
                              Blocked
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Source:</span>
                            <span className="ml-2 font-mono font-medium">{threat.source_ip}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Target:</span>
                            <span className="ml-2 font-mono font-medium">{threat.destination_ip}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Confidence:</span>
                            <span className="ml-2 font-medium">{(threat.confidence * 100).toFixed(1)}%</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Time:</span>
                            <span className="ml-2">{new Date(threat.timestamp).toLocaleString()}</span>
                          </div>
                        </div>
                        
                        <p className="text-gray-700 mt-2">{threat.description}</p>
                      </div>
                      
                      <div className="ml-4">
                        <ExternalLink className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <div className="text-sm text-gray-600">
                  Showing {((currentPage - 1) * threatsPerPage) + 1} to {Math.min(currentPage * threatsPerPage, totalThreats)} of {totalThreats} threats
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </Button>
                  
                  <div className="flex items-center space-x-1">
                    {[...Array(Math.min(5, totalPages))].map((_, i) => {
                      const pageNum = Math.max(1, currentPage - 2) + i;
                      if (pageNum > totalPages) return null;
                      
                      return (
                        <Button
                          key={pageNum}
                          variant={pageNum === currentPage ? "default" : "outline"}
                          size="sm"
                          onClick={() => setCurrentPage(pageNum)}
                          className="w-8 h-8 p-0"
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
