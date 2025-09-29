// START OF FILE web/src/pages/NetworkVisualizationPage.tsx
/**
 * HAI-Net Network Visualization Page
 * Constitutional compliance: Decentralization + Community Focus
 * Real-time visualization of decentralized network topology
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Refresh,
  Hub,
  Computer,
  Security,
  Speed,
  People,
} from '@mui/icons-material';

// Services
import { APIService } from '../services/APIService';

// Types
interface NetworkVisualizationPageProps {
  apiService: APIService;
}

interface NetworkNode {
  id: string;
  type: 'local' | 'peer' | 'hub';
  status: 'active' | 'inactive' | 'connecting';
  constitutional_compliant: boolean;
  connections: number;
  uptime: number;
  location?: { x: number; y: number };
}

interface NetworkMetrics {
  total_nodes: number;
  active_connections: number;
  constitutional_compliance: number;
  network_health: number;
  data_throughput: number;
}

const NetworkVisualizationPage: React.FC<NetworkVisualizationPageProps> = ({ apiService }) => {
  // State
  const [networkNodes, setNetworkNodes] = useState<NetworkNode[]>([]);
  const [networkMetrics, setNetworkMetrics] = useState<NetworkMetrics>({
    total_nodes: 1,
    active_connections: 0,
    constitutional_compliance: 1.0,
    network_health: 1.0,
    data_throughput: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Canvas ref for WebGL/Canvas rendering
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Initialize network data
  useEffect(() => {
    loadNetworkData();
    
    // Set up periodic refresh
    const interval = setInterval(loadNetworkData, 10000); // Refresh every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Initialize network visualization
  useEffect(() => {
    if (canvasRef.current) {
      initializeNetworkVisualization();
    }
  }, [networkNodes]);

  const loadNetworkData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get network status
      const networkStatus = await apiService.getNetworkStatus();
      
      // Simulate network nodes (in real implementation, this would come from P2P discovery)
      const simulatedNodes: NetworkNode[] = [
        {
          id: 'local_hub',
          type: 'local',
          status: 'active',
          constitutional_compliant: true,
          connections: networkStatus.connected_peers,
          uptime: Date.now() - 3600000, // 1 hour ago
          location: { x: 50, y: 50 }, // Center
        },
      ];

      // Add discovered peers (simulated)
      for (let i = 0; i < networkStatus.connected_peers; i++) {
        simulatedNodes.push({
          id: `peer_${i + 1}`,
          type: 'peer',
          status: 'active',
          constitutional_compliant: Math.random() > 0.1, // 90% compliance
          connections: Math.floor(Math.random() * 5) + 1,
          uptime: Date.now() - Math.random() * 7200000, // Random uptime up to 2 hours
          location: {
            x: 30 + Math.random() * 40,
            y: 30 + Math.random() * 40,
          },
        });
      }

      setNetworkNodes(simulatedNodes);

      // Update metrics
      const compliantNodes = simulatedNodes.filter(n => n.constitutional_compliant).length;
      setNetworkMetrics({
        total_nodes: simulatedNodes.length,
        active_connections: networkStatus.connected_peers,
        constitutional_compliance: compliantNodes / simulatedNodes.length,
        network_health: networkStatus.discovery_active ? 1.0 : 0.5,
        data_throughput: Math.random() * 100, // Simulated throughput
      });

    } catch (err) {
      setError(`Failed to load network data: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const initializeNetworkVisualization = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Constitutional color scheme
    const colors = {
      local: '#4CAF50',      // Constitutional green
      peer: '#2196F3',       // Trust blue
      connection: '#666',    // Connection gray
      violation: '#F44336',  // Violation red
      background: '#1e1e1e', // Dark background
    };

    // Set background
    ctx.fillStyle = colors.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw connections first (so they appear behind nodes)
    networkNodes.forEach(node => {
      if (node.type === 'local') return; // Local node is center, draw connections to it
      
      const localNode = networkNodes.find(n => n.type === 'local');
      if (!localNode || !localNode.location || !node.location) return;

      const startX = (localNode.location.x / 100) * canvas.width;
      const startY = (localNode.location.y / 100) * canvas.height;
      const endX = (node.location.x / 100) * canvas.width;
      const endY = (node.location.y / 100) * canvas.height;

      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = node.constitutional_compliant ? colors.connection : colors.violation;
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Draw nodes
    networkNodes.forEach(node => {
      if (!node.location) return;

      const x = (node.location.x / 100) * canvas.width;
      const y = (node.location.y / 100) * canvas.height;
      const radius = node.type === 'local' ? 20 : 12;

      // Node circle
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = node.constitutional_compliant ? 
        (node.type === 'local' ? colors.local : colors.peer) : 
        colors.violation;
      ctx.fill();

      // Node border
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = node.status === 'active' ? '#fff' : '#888';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Node label
      ctx.fillStyle = '#fff';
      ctx.font = '10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(node.id.split('_')[0], x, y + radius + 15);
    });

    // Draw constitutional compliance indicator
    const complianceText = `Constitutional Compliance: ${(networkMetrics.constitutional_compliance * 100).toFixed(1)}%`;
    ctx.fillStyle = networkMetrics.constitutional_compliance > 0.8 ? colors.local : colors.violation;
    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(complianceText, 10, 25);
  };

  const handleRefresh = () => {
    loadNetworkData();
  };

  const getStatusColor = (value: number): string => {
    if (value >= 0.9) return '#4CAF50'; // Green
    if (value >= 0.7) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const formatUptime = (timestamp: number): string => {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" sx={{ color: '#4CAF50' }}>
          Decentralized Network
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh network data">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Network Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Hub color="primary" />
                <Box>
                  <Typography variant="h6">{networkMetrics.total_nodes}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Network Nodes
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Computer color="primary" />
                <Box>
                  <Typography variant="h6">{networkMetrics.active_connections}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active Connections
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Security sx={{ color: getStatusColor(networkMetrics.constitutional_compliance) }} />
                <Box>
                  <Typography 
                    variant="h6" 
                    sx={{ color: getStatusColor(networkMetrics.constitutional_compliance) }}
                  >
                    {(networkMetrics.constitutional_compliance * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Constitutional Compliance
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed sx={{ color: getStatusColor(networkMetrics.network_health) }} />
                <Box>
                  <Typography 
                    variant="h6"
                    sx={{ color: getStatusColor(networkMetrics.network_health) }}
                  >
                    {(networkMetrics.network_health * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Network Health
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Network Visualization */}
      <Grid container spacing={2}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Network Topology
              </Typography>
              <Box sx={{ position: 'relative', height: 320 }}>
                <canvas
                  ref={canvasRef}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: '1px solid #333',
                    borderRadius: 4,
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Network Nodes
              </Typography>
              <Box sx={{ maxHeight: 320, overflow: 'auto' }}>
                {networkNodes.map((node) => (
                  <Box
                    key={node.id}
                    sx={{
                      p: 1,
                      mb: 1,
                      border: '1px solid #333',
                      borderRadius: 1,
                      backgroundColor: '#2a2a2a',
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" fontWeight="bold">
                        {node.id}
                      </Typography>
                      <Chip
                        label={node.type}
                        size="small"
                        color={node.type === 'local' ? 'primary' : 'default'}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      <Typography variant="caption">
                        Status: {node.status}
                      </Typography>
                      <Typography variant="caption">
                        Uptime: {formatUptime(node.uptime)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                      <Typography variant="caption">
                        Connections: {node.connections}
                      </Typography>
                      <Chip
                        label={node.constitutional_compliant ? 'Compliant' : 'Violation'}
                        size="small"
                        color={node.constitutional_compliant ? 'success' : 'error'}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Constitutional Principles Footer */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Constitutional Principles in Action:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip icon={<Security />} label="Privacy First" size="small" />
          <Chip icon={<People />} label="Human Rights" size="small" />
          <Chip icon={<Hub />} label="Decentralization" size="small" />
          <Chip icon={<Computer />} label="Community Focus" size="small" />
        </Box>
      </Box>
    </Box>
  );
};

export default NetworkVisualizationPage;
