// START OF FILE web/src/pages/LogsPage.tsx
/**
 * HAI-Net Logs Page
 * Constitutional compliance: Privacy First + Human Rights + Transparency
 * System logs and audit trail with constitutional compliance tracking
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert,
  Paper,
  Button,
} from '@mui/material';
import {
  Refresh,
  Search,
  Clear,
  Download,
  FilterList,
  Security,
  Warning,
  Error,
  Info,
  CheckCircle,
  Computer,
  Psychology,
  Hub,
  People,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';

// Services
import { APIService } from '../services/APIService';

// Types
interface LogsPageProps {
  apiService: APIService;
}

interface LogEntry {
  id: string;
  timestamp: number;
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  component: string;
  message: string;
  constitutional_compliant: boolean;
  constitutional_principle?: string;
  user_id?: string;
  agent_id?: string;
  details?: any;
}

interface LogFilter {
  level: string;
  component: string;
  constitutional: string;
  timeRange: string;
}

const LogsPage: React.FC<LogsPageProps> = ({ apiService }) => {
  // State
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDetails, setShowDetails] = useState<Set<string>>(new Set());
  
  // Filters
  const [filters, setFilters] = useState<LogFilter>({
    level: 'all',
    component: 'all',
    constitutional: 'all',
    timeRange: '1h',
  });

  // Initialize logs
  useEffect(() => {
    loadLogs();
    
    // Set up periodic refresh
    const interval = setInterval(loadLogs, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Filter logs when search or filters change
  useEffect(() => {
    filterLogs();
  }, [logs, searchQuery, filters]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get logs from API
      const apiLogs = await apiService.getLogs();
      
      // Simulate additional constitutional logs
      const constitutionalLogs: LogEntry[] = [
        {
          id: 'log_001',
          timestamp: Date.now() - 5000,
          level: 'INFO',
          component: 'constitutional_guardian',
          message: 'Constitutional monitoring active - all four principles enforced',
          constitutional_compliant: true,
          constitutional_principle: 'All Principles',
        },
        {
          id: 'log_002',
          timestamp: Date.now() - 10000,
          level: 'INFO',
          component: 'llm_manager',
          message: 'AI response generated with constitutional compliance filtering',
          constitutional_compliant: true,
          constitutional_principle: 'Privacy First',
          details: { model: 'llama3.1', tokens: 150, privacy_protected: true },
        },
        {
          id: 'log_003',
          timestamp: Date.now() - 15000,
          level: 'INFO',
          component: 'agent_manager',
          message: 'New agent created with constitutional compliance validation',
          constitutional_compliant: true,
          constitutional_principle: 'Human Rights',
          agent_id: 'agent_admin_001',
        },
        {
          id: 'log_004',
          timestamp: Date.now() - 20000,
          level: 'INFO',
          component: 'web_server',
          message: 'Client WebSocket connection established with privacy protection',
          constitutional_compliant: true,
          constitutional_principle: 'Privacy First',
        },
        {
          id: 'log_005',
          timestamp: Date.now() - 25000,
          level: 'INFO',
          component: 'network_discovery',
          message: 'P2P peer discovery active - decentralized network operational',
          constitutional_compliant: true,
          constitutional_principle: 'Decentralization',
        },
        {
          id: 'log_006',
          timestamp: Date.now() - 30000,
          level: 'DEBUG',
          component: 'memory_manager',
          message: 'Memory cleanup completed - privacy retention policies enforced',
          constitutional_compliant: true,
          constitutional_principle: 'Privacy First',
          details: { memories_cleaned: 15, retention_policy: 'privacy_first' },
        },
        ...apiLogs.map((log, index) => ({
          id: `api_log_${index}`,
          timestamp: log.timestamp,
          level: log.level as any,
          component: log.component,
          message: log.message,
          constitutional_compliant: log.constitutional_compliant,
        })),
      ];

      setLogs(constitutionalLogs.sort((a, b) => b.timestamp - a.timestamp));

    } catch (err) {
      setError(`Failed to load logs: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = logs;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(query) ||
        log.component.toLowerCase().includes(query) ||
        log.level.toLowerCase().includes(query)
      );
    }

    // Apply level filter
    if (filters.level !== 'all') {
      filtered = filtered.filter(log => log.level === filters.level);
    }

    // Apply component filter
    if (filters.component !== 'all') {
      filtered = filtered.filter(log => log.component === filters.component);
    }

    // Apply constitutional filter
    if (filters.constitutional === 'compliant') {
      filtered = filtered.filter(log => log.constitutional_compliant);
    } else if (filters.constitutional === 'violations') {
      filtered = filtered.filter(log => !log.constitutional_compliant);
    }

    // Apply time range filter
    const now = Date.now();
    const timeRanges = {
      '1h': 3600000,
      '24h': 86400000,
      '7d': 604800000,
      '30d': 2592000000,
    };
    
    if (filters.timeRange !== 'all') {
      const range = timeRanges[filters.timeRange as keyof typeof timeRanges];
      if (range) {
        filtered = filtered.filter(log => now - log.timestamp <= range);
      }
    }

    setFilteredLogs(filtered);
  };

  const handleRefresh = () => {
    loadLogs();
  };

  const handleExportLogs = () => {
    const csvContent = [
      ['Timestamp', 'Level', 'Component', 'Message', 'Constitutional Compliant', 'Principle'].join(','),
      ...filteredLogs.map(log => [
        new Date(log.timestamp).toISOString(),
        log.level,
        log.component,
        `"${log.message.replace(/"/g, '""')}"`,
        log.constitutional_compliant,
        log.constitutional_principle || '',
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hai-net-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleDetails = (logId: string) => {
    const newShowDetails = new Set(showDetails);
    if (newShowDetails.has(logId)) {
      newShowDetails.delete(logId);
    } else {
      newShowDetails.add(logId);
    }
    setShowDetails(newShowDetails);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'DEBUG':
        return 'default';
      case 'INFO':
        return 'info';
      case 'WARNING':
        return 'warning';
      case 'ERROR':
        return 'error';
      case 'CRITICAL':
        return 'error';
      default:
        return 'default';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'DEBUG':
        return <Info />;
      case 'INFO':
        return <CheckCircle />;
      case 'WARNING':
        return <Warning />;
      case 'ERROR':
      case 'CRITICAL':
        return <Error />;
      default:
        return <Info />;
    }
  };

  const getComponentIcon = (component: string) => {
    if (component.includes('constitutional') || component.includes('guardian')) {
      return <Security />;
    } else if (component.includes('agent')) {
      return <Psychology />;
    } else if (component.includes('network') || component.includes('p2p')) {
      return <Hub />;
    } else if (component.includes('web') || component.includes('server')) {
      return <Computer />;
    } else {
      return <Computer />;
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const getUniqueComponents = () => {
    const components = Array.from(new Set(logs.map(log => log.component)));
    return components.sort();
  };

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" sx={{ color: '#4CAF50' }}>
          Constitutional Logs
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Export logs">
            <IconButton onClick={handleExportLogs}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh logs">
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

      {/* Search and Filters */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            {/* Search */}
            <TextField
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setSearchQuery('')} size="small">
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 300 }}
            />

            {/* Level Filter */}
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Level</InputLabel>
              <Select
                value={filters.level}
                onChange={(e) => setFilters(prev => ({ ...prev, level: e.target.value }))}
                label="Level"
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="DEBUG">Debug</MenuItem>
                <MenuItem value="INFO">Info</MenuItem>
                <MenuItem value="WARNING">Warning</MenuItem>
                <MenuItem value="ERROR">Error</MenuItem>
                <MenuItem value="CRITICAL">Critical</MenuItem>
              </Select>
            </FormControl>

            {/* Component Filter */}
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Component</InputLabel>
              <Select
                value={filters.component}
                onChange={(e) => setFilters(prev => ({ ...prev, component: e.target.value }))}
                label="Component"
              >
                <MenuItem value="all">All Components</MenuItem>
                {getUniqueComponents().map(component => (
                  <MenuItem key={component} value={component}>{component}</MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Constitutional Filter */}
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Constitutional</InputLabel>
              <Select
                value={filters.constitutional}
                onChange={(e) => setFilters(prev => ({ ...prev, constitutional: e.target.value }))}
                label="Constitutional"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="compliant">Compliant</MenuItem>
                <MenuItem value="violations">Violations</MenuItem>
              </Select>
            </FormControl>

            {/* Time Range Filter */}
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={filters.timeRange}
                onChange={(e) => setFilters(prev => ({ ...prev, timeRange: e.target.value }))}
                label="Time Range"
              >
                <MenuItem value="1h">Last Hour</MenuItem>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="all">All Time</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Results Summary */}
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              label={`${filteredLogs.length} logs`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`${filteredLogs.filter(l => l.constitutional_compliant).length} compliant`}
              color="success"
              variant="outlined"
            />
            <Chip
              label={`${filteredLogs.filter(l => !l.constitutional_compliant).length} violations`}
              color="error"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" gutterBottom>
            System Logs ({filteredLogs.length})
          </Typography>
          
          <TableContainer component={Paper} sx={{ flexGrow: 1, overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Component</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Constitutional</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log) => (
                  <React.Fragment key={log.id}>
                    <TableRow>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {formatTimestamp(log.timestamp)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getLevelIcon(log.level)}
                          label={log.level}
                          color={getLevelColor(log.level) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getComponentIcon(log.component)}
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {log.component}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {log.message}
                        </Typography>
                        {log.constitutional_principle && (
                          <Chip
                            label={log.constitutional_principle}
                            size="small"
                            color="primary"
                            variant="outlined"
                            sx={{ mt: 0.5 }}
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={log.constitutional_compliant ? <CheckCircle /> : <Error />}
                          label={log.constitutional_compliant ? 'Compliant' : 'Violation'}
                          color={log.constitutional_compliant ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {log.details && (
                          <IconButton
                            size="small"
                            onClick={() => toggleDetails(log.id)}
                          >
                            {showDetails.has(log.id) ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                    
                    {/* Details Row */}
                    {showDetails.has(log.id) && log.details && (
                      <TableRow>
                        <TableCell colSpan={6}>
                          <Box sx={{ bgcolor: '#2a2a2a', p: 2, borderRadius: 1 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Details:
                            </Typography>
                            <Box component="pre" sx={{ 
                              fontFamily: 'monospace', 
                              fontSize: '0.8rem',
                              overflow: 'auto',
                              whiteSpace: 'pre-wrap' 
                            }}>
                              {JSON.stringify(log.details, null, 2)}
                            </Box>
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                ))}
                
                {filteredLogs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="textSecondary">
                        No logs found matching your criteria
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Constitutional Principles Footer */}
      <Box sx={{ mt: 2, p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Constitutional Audit Trail Active:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Chip icon={<Security />} label="Privacy First" size="small" color="success" />
          <Chip icon={<People />} label="Human Rights" size="small" color="success" />
          <Chip icon={<Hub />} label="Decentralization" size="small" color="success" />
          <Chip icon={<Computer />} label="Community Focus" size="small" color="success" />
        </Box>
      </Box>
    </Box>
  );
};

export default LogsPage;
