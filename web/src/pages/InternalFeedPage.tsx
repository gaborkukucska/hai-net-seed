// START OF FILE web/src/pages/InternalFeedPage.tsx
/**
 * HAI-Net Internal Feed Page
 * Constitutional compliance: Privacy First + Human Rights + Community Focus
 * Real-time feed of constitutional AI activities and events
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  TextField,
  InputAdornment,
  Fab,
} from '@mui/material';
import {
  Security,
  Psychology,
  Hub,
  People,
  Search,
  Clear,
  Chat,
  Computer,
  Shield,
  Warning,
  CheckCircle,
  Error,
  Info,
} from '@mui/icons-material';

// Services
import { WebSocketService } from '../services/WebSocketService';

// Types
interface InternalFeedPageProps {
  webSocketService: WebSocketService;
}

interface FeedEvent {
  id: string;
  timestamp: number;
  type: 'constitutional' | 'agent' | 'chat' | 'network' | 'system';
  severity: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  component: string;
  constitutional_compliant: boolean;
  details?: any;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  constitutional_compliant: boolean;
}

const InternalFeedPage: React.FC<InternalFeedPageProps> = ({ webSocketService }) => {
  // State
  const [feedEvents, setFeedEvents] = useState<FeedEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<FeedEvent[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  // Initialize feed data
  useEffect(() => {
    loadInitialFeedData();
    
    // Set up WebSocket event handlers
    webSocketService.onMessage((message) => {
      handleWebSocketMessage(message);
    });

    webSocketService.onConstitutionalUpdate((status) => {
      addFeedEvent({
        type: 'constitutional',
        severity: status.compliance_score > 0.8 ? 'success' : 'warning',
        title: 'Constitutional Update',
        message: `Compliance score: ${(status.compliance_score * 100).toFixed(1)}%`,
        component: 'constitutional_guardian',
        constitutional_compliant: status.compliance_score > 0.8,
        details: status,
      });
    });

    webSocketService.onAgentUpdate((update) => {
      addFeedEvent({
        type: 'agent',
        severity: update.constitutional_compliant ? 'info' : 'warning',
        title: 'Agent Update',
        message: `Agent ${update.agent_id} state: ${update.state}`,
        component: 'agent_manager',
        constitutional_compliant: update.constitutional_compliant,
        details: update,
      });
    });

  }, [webSocketService]);

  // Filter events when search or filter changes
  useEffect(() => {
    filterEvents();
  }, [feedEvents, searchQuery, selectedFilter]);

  const loadInitialFeedData = () => {
    // Load initial feed events (simulated)
    const initialEvents: FeedEvent[] = [
      {
        id: 'feed_001',
        timestamp: Date.now() - 1000,
        type: 'system',
        severity: 'success',
        title: 'Constitutional AI Started',
        message: 'HAI-Net Constitutional AI system initialized successfully',
        component: 'web_server',
        constitutional_compliant: true,
      },
      {
        id: 'feed_002',
        timestamp: Date.now() - 2000,
        type: 'constitutional',
        severity: 'info',
        title: 'Guardian Monitoring Active',
        message: 'Constitutional Guardian agent is actively monitoring compliance',
        component: 'constitutional_guardian',
        constitutional_compliant: true,
      },
      {
        id: 'feed_003',
        timestamp: Date.now() - 3000,
        type: 'agent',
        severity: 'success',
        title: 'Agent Created',
        message: 'New admin agent created with constitutional compliance',
        component: 'agent_manager',
        constitutional_compliant: true,
      },
    ];

    setFeedEvents(initialEvents);
  };

  const handleWebSocketMessage = (message: any) => {
    // Handle various WebSocket message types
    if (message.type === 'feed_event') {
      addFeedEvent(message.data);
    }
  };

  const addFeedEvent = (eventData: Partial<FeedEvent>) => {
    const newEvent: FeedEvent = {
      id: `feed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      type: 'system',
      severity: 'info',
      constitutional_compliant: true,
      ...eventData,
    } as FeedEvent;

    setFeedEvents(prev => [newEvent, ...prev].slice(0, 100)); // Keep last 100 events
  };

  const filterEvents = () => {
    let filtered = feedEvents;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(event =>
        event.title.toLowerCase().includes(query) ||
        event.message.toLowerCase().includes(query) ||
        event.component.toLowerCase().includes(query)
      );
    }

    // Apply type filter
    if (selectedFilter !== 'all') {
      filtered = filtered.filter(event => event.type === selectedFilter);
    }

    setFilteredEvents(filtered);
  };

  const getEventIcon = (event: FeedEvent) => {
    switch (event.type) {
      case 'constitutional':
        return <Security color={event.constitutional_compliant ? 'success' : 'error'} />;
      case 'agent':
        return <Psychology color={event.constitutional_compliant ? 'primary' : 'warning'} />;
      case 'chat':
        return <Chat color="info" />;
      case 'network':
        return <Hub color="primary" />;
      case 'system':
      default:
        return <Computer color="info" />;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'success':
        return <CheckCircle color="success" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      case 'info':
      default:
        return <Info color="info" />;
    }
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);

    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const getFilterOptions = () => [
    { value: 'all', label: 'All Events', count: feedEvents.length },
    { value: 'constitutional', label: 'Constitutional', count: feedEvents.filter(e => e.type === 'constitutional').length },
    { value: 'agent', label: 'Agents', count: feedEvents.filter(e => e.type === 'agent').length },
    { value: 'chat', label: 'Chat', count: feedEvents.filter(e => e.type === 'chat').length },
    { value: 'network', label: 'Network', count: feedEvents.filter(e => e.type === 'network').length },
    { value: 'system', label: 'System', count: feedEvents.filter(e => e.type === 'system').length },
  ];

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" sx={{ color: '#4CAF50' }}>
          Constitutional AI Feed
        </Typography>
        <Chip
          icon={<Shield />}
          label="Privacy Protected"
          color="success"
          variant="outlined"
        />
      </Box>

      {/* Search and Filters */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Search events..."
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
          sx={{ mb: 2 }}
        />

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {getFilterOptions().map((option) => (
            <Chip
              key={option.value}
              label={`${option.label} (${option.count})`}
              onClick={() => setSelectedFilter(option.value)}
              color={selectedFilter === option.value ? 'primary' : 'default'}
              variant={selectedFilter === option.value ? 'filled' : 'outlined'}
            />
          ))}
        </Box>
      </Box>

      {/* Main Content - Events Feed */}
      <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" gutterBottom>
            Live Events ({filteredEvents.length})
          </Typography>
          <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
            <List>
              {filteredEvents.map((event) => (
                <ListItem key={event.id} divider>
                  <ListItemIcon>
                    {getEventIcon(event)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle2">
                          {event.title}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getSeverityIcon(event.severity)}
                          <Typography variant="caption" color="textSecondary">
                            {formatTimestamp(event.timestamp)}
                          </Typography>
                        </Box>
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {event.message}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip
                            label={event.component}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={event.constitutional_compliant ? 'Compliant' : 'Violation'}
                            size="small"
                            color={event.constitutional_compliant ? 'success' : 'error'}
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
              {filteredEvents.length === 0 && (
                <ListItem>
                  <ListItemText
                    primary="No events found"
                    secondary="No events match your current filter criteria"
                  />
                </ListItem>
              )}
            </List>
          </Box>
        </CardContent>
      </Card>

      {/* Constitutional Principles Footer */}
      <Box sx={{ mt: 2, p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Constitutional AI Monitoring Active:
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

export default InternalFeedPage;
