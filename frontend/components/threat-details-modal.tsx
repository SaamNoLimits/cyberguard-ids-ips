'use client';

import React, { useState, useEffect } from 'react';
import { X, Shield, AlertTriangle, Info, CheckCircle, XCircle, Clock, Network, Eye, Lock, Unlock } from 'lucide-react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { apiClient } from '@/lib/api';

interface ThreatDetailsModalProps {
  threatId: string;
  isOpen: boolean;
  onClose: () => void;
  onBlock?: (threatId: string) => void;
  onUnblock?: (threatId: string) => void;
}

interface ThreatDetails {
  threat_info: {
    id: string;
    timestamp: string;
    source_ip: string;
    destination_ip: string;
    attack_type: string;
    threat_level: string;
    confidence: number;
    description: string;
    blocked: boolean;
  };
  packet_analysis: {
    protocol: string;
    packet_size: number;
    ttl: number;
    source_port?: number;
    destination_port?: number;
    tcp_flags?: string;
    window_size?: number;
    icmp_type?: number;
    icmp_code?: number;
  };
  risk_assessment: {
    severity: string;
    confidence_score: number;
    potential_impact: string;
    attack_vector: string;
  };
  recommendations: string[];
  mitigation_steps: string[];
}

export function ThreatDetailsModal({ threatId, isOpen, onClose, onBlock, onUnblock }: ThreatDetailsModalProps) {
  const [details, setDetails] = useState<ThreatDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const api = apiClient;

  useEffect(() => {
    if (isOpen && threatId) {
      fetchThreatDetails();
    }
  }, [isOpen, threatId]);

  const fetchThreatDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getThreatDetails(threatId);
      setDetails(response);
    } catch (err) {
      setError('Failed to fetch threat details');
      console.error('Error fetching threat details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBlock = async () => {
    if (!details) return;
    
    setActionLoading(true);
    try {
      await api.blockThreat(threatId);
      setDetails(prev => prev ? {
        ...prev,
        threat_info: { ...prev.threat_info, blocked: true }
      } : null);
      onBlock?.(threatId);
    } catch (err) {
      console.error('Error blocking threat:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnblock = async () => {
    if (!details) return;
    
    setActionLoading(true);
    try {
      await api.unblockThreat(threatId);
      setDetails(prev => prev ? {
        ...prev,
        threat_info: { ...prev.threat_info, blocked: false }
      } : null);
      onUnblock?.(threatId);
    } catch (err) {
      console.error('Error unblocking threat:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-6 w-6 text-red-500" />
            <h2 className="text-xl font-semibold">Threat Details</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3">Loading threat details...</span>
            </div>
          ) : error ? (
            <div className="p-6 text-center">
              <div className="text-red-500 mb-2">
                <XCircle className="h-12 w-12 mx-auto" />
              </div>
              <p className="text-red-600">{error}</p>
              <Button onClick={fetchThreatDetails} className="mt-4">
                Retry
              </Button>
            </div>
          ) : details ? (
            <div className="p-6">
              {/* Quick Actions */}
              <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <Badge className={getSeverityColor(details.threat_info.threat_level)}>
                    {details.threat_info.threat_level}
                  </Badge>
                  <Badge variant={details.threat_info.blocked ? "destructive" : "secondary"}>
                    {details.threat_info.blocked ? (
                      <>
                        <Lock className="h-3 w-3 mr-1" />
                        Blocked
                      </>
                    ) : (
                      <>
                        <Unlock className="h-3 w-3 mr-1" />
                        Active
                      </>
                    )}
                  </Badge>
                  <span className="text-sm text-gray-600">
                    Confidence: {(details.threat_info.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex space-x-2">
                  {details.threat_info.blocked ? (
                    <Button
                      onClick={handleUnblock}
                      disabled={actionLoading}
                      variant="outline"
                      size="sm"
                    >
                      <Unlock className="h-4 w-4 mr-2" />
                      Unblock
                    </Button>
                  ) : (
                    <Button
                      onClick={handleBlock}
                      disabled={actionLoading}
                      variant="destructive"
                      size="sm"
                    >
                      <Lock className="h-4 w-4 mr-2" />
                      Block Threat
                    </Button>
                  )}
                </div>
              </div>

              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="analysis">Analysis</TabsTrigger>
                  <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                  <TabsTrigger value="mitigation">Mitigation</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium flex items-center">
                          <Info className="h-4 w-4 mr-2" />
                          Basic Information
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Threat ID:</span>
                          <span className="text-sm font-mono">{details.threat_info.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Detected:</span>
                          <span className="text-sm">{formatTimestamp(details.threat_info.timestamp)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Attack Type:</span>
                          <span className="text-sm font-medium">{details.threat_info.attack_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Source IP:</span>
                          <span className="text-sm font-mono">{details.threat_info.source_ip}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Target IP:</span>
                          <span className="text-sm font-mono">{details.threat_info.destination_ip}</span>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium flex items-center">
                          <Network className="h-4 w-4 mr-2" />
                          Network Details
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Protocol:</span>
                          <span className="text-sm">{details.packet_analysis.protocol}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Packet Size:</span>
                          <span className="text-sm">{details.packet_analysis.packet_size} bytes</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">TTL:</span>
                          <span className="text-sm">{details.packet_analysis.ttl}</span>
                        </div>
                        {details.packet_analysis.source_port && (
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Source Port:</span>
                            <span className="text-sm">{details.packet_analysis.source_port}</span>
                          </div>
                        )}
                        {details.packet_analysis.destination_port && (
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Dest Port:</span>
                            <span className="text-sm">{details.packet_analysis.destination_port}</span>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium">Description</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700">{details.threat_info.description}</p>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="analysis" className="space-y-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium flex items-center">
                        <Eye className="h-4 w-4 mr-2" />
                        Risk Assessment
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">Attack Vector</h4>
                        <p className="text-sm text-gray-700">{details.risk_assessment.attack_vector}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium mb-2">Potential Impact</h4>
                        <p className="text-sm text-gray-700">{details.risk_assessment.potential_impact}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-sm font-medium mb-2">Severity Level</h4>
                          <Badge className={getSeverityColor(details.risk_assessment.severity)}>
                            {details.risk_assessment.severity}
                          </Badge>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium mb-2">Confidence Score</h4>
                          <div className="flex items-center">
                            <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${details.risk_assessment.confidence_score * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm">{(details.risk_assessment.confidence_score * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="recommendations" className="space-y-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium flex items-center">
                        <Shield className="h-4 w-4 mr-2" />
                        Security Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {details.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="mitigation" className="space-y-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium flex items-center">
                        <Clock className="h-4 w-4 mr-2" />
                        Immediate Mitigation Steps
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ol className="space-y-3">
                        {details.mitigation_steps.map((step, index) => (
                          <li key={index} className="flex items-start">
                            <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                              {index + 1}
                            </div>
                            <span className="text-sm text-gray-700">{step}</span>
                          </li>
                        ))}
                      </ol>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t bg-gray-50">
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
