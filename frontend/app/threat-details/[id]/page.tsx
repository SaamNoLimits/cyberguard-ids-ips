'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  Shield, 
  AlertTriangle, 
  Clock, 
  MapPin, 
  Network,
  Eye,
  Ban,
  CheckCircle,
  XCircle,
  Activity,
  Globe
} from 'lucide-react';

interface ThreatDetails {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  attack_type: string;
  threat_level: string;
  confidence: number;
  description: string;
  blocked: boolean;
  raw_data: any;
  analysis: {
    severity_score: number;
    risk_assessment: string;
    recommended_actions: string[];
    similar_attacks: any[];
    geolocation: any;
    threat_intelligence: any;
  };
}

export default function ThreatDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const [threat, setThreat] = useState<ThreatDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreatDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/public/threats/${params.id}`);
        if (!response.ok) {
          throw new Error('Threat not found');
        }
        const data = await response.json();
        setThreat(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load threat details');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchThreatDetails();
    }
  }, [params.id]);

  const getThreatLevelColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return 'bg-red-500';
      case 'HIGH': return 'bg-orange-500';
      case 'MEDIUM': return 'bg-yellow-500';
      case 'LOW': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskColor = (assessment: string) => {
    if (assessment?.includes('EXTREME')) return 'text-red-600';
    if (assessment?.includes('HIGH')) return 'text-orange-600';
    if (assessment?.includes('MODERATE')) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="h-64 bg-gray-200 rounded"></div>
                <div className="h-48 bg-gray-200 rounded"></div>
              </div>
              <div className="space-y-6">
                <div className="h-32 bg-gray-200 rounded"></div>
                <div className="h-48 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !threat) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <Button 
            onClick={() => router.back()} 
            variant="outline" 
            className="mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <Card>
            <CardContent className="p-12 text-center">
              <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Threat Not Found</h2>
              <p className="text-gray-600">{error || 'The requested threat could not be found.'}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button 
              onClick={() => router.back()} 
              variant="outline"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Threat Analysis</h1>
              <p className="text-gray-600">Detailed analysis of security threat #{threat.id.slice(-8)}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getThreatLevelColor(threat.threat_level)}>
              {threat.threat_level}
            </Badge>
            {threat.blocked ? (
              <Badge variant="destructive">
                <Ban className="w-3 h-3 mr-1" />
                Blocked
              </Badge>
            ) : (
              <Badge variant="secondary">
                <Eye className="w-3 h-3 mr-1" />
                Monitoring
              </Badge>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Threat Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Threat Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Attack Type</label>
                    <p className="text-lg font-semibold">{threat.attack_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Confidence Level</label>
                    <p className="text-lg font-semibold">{(threat.confidence * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Source IP</label>
                    <p className="text-lg font-semibold font-mono">{threat.source_ip}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Target IP</label>
                    <p className="text-lg font-semibold font-mono">{threat.destination_ip}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Detection Time</label>
                    <p className="text-lg font-semibold">
                      {new Date(threat.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Severity Score</label>
                    <p className="text-lg font-semibold">{threat.analysis.severity_score.toFixed(0)}/100</p>
                  </div>
                </div>
                <Separator />
                <div>
                  <label className="text-sm font-medium text-gray-500">Description</label>
                  <p className="text-gray-900 mt-1">{threat.description}</p>
                </div>
              </CardContent>
            </Card>

            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <p className={`text-lg font-semibold ${getRiskColor(threat.analysis.risk_assessment)}`}>
                    {threat.analysis.risk_assessment}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Recommended Actions:</h4>
                  <ul className="space-y-2">
                    {threat.analysis.recommended_actions.map((action, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                        <span className="text-sm">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Similar Attacks */}
            {threat.analysis.similar_attacks.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    Similar Attacks ({threat.analysis.similar_attacks.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {threat.analysis.similar_attacks.map((attack, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium">{attack.attack_type}</p>
                          <p className="text-sm text-gray-600">
                            From {attack.source_ip} • {new Date(attack.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <Badge variant="outline">
                          {(attack.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status</span>
                  <Badge variant={threat.blocked ? "destructive" : "secondary"}>
                    {threat.blocked ? "Blocked" : "Active"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Threat Level</span>
                  <Badge className={getThreatLevelColor(threat.threat_level)}>
                    {threat.threat_level}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Confidence</span>
                  <span className="font-semibold">{(threat.confidence * 100).toFixed(1)}%</span>
                </div>
              </CardContent>
            </Card>

            {/* Geolocation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <MapPin className="w-4 h-4 mr-2" />
                  Source Location
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500">Country</label>
                  <p className="font-medium">{threat.analysis.geolocation.country || 'Unknown'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Region</label>
                  <p className="font-medium">{threat.analysis.geolocation.region || 'Unknown'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500">ISP</label>
                  <p className="font-medium">{threat.analysis.geolocation.isp || 'Unknown'}</p>
                </div>
              </CardContent>
            </Card>

            {/* Threat Intelligence */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Globe className="w-4 h-4 mr-2" />
                  Threat Intelligence
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500">Reputation Score</label>
                  <p className="font-medium">{threat.analysis.threat_intelligence.reputation_score}/100</p>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Known Malicious</label>
                  <p className="font-medium">
                    {threat.analysis.threat_intelligence.known_malicious ? 'Yes' : 'No'}
                  </p>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Reports</label>
                  <p className="font-medium">{threat.analysis.threat_intelligence.reports_count}</p>
                </div>
              </CardContent>
            </Card>

            {/* Raw Data */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Network className="w-4 h-4 mr-2" />
                  Technical Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                  {JSON.stringify(threat.raw_data, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
