// START OF FILE web/src/App.tsx
/**
 * HAI-Net Constitutional AI Interface
 * Constitutional compliance: Privacy First + Human Rights + Community Focus
 * Main React application with 4-page constitutional design
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, BottomNavigation, BottomNavigationAction, Alert, Snackbar } from '@mui/material';
import { AccountTree, Timeline, Terminal, Settings, Security, Chat } from '@mui/icons-material';

// Constitutional pages
import { 
  ChatPage,
  NetworkVisualizationPage,
  InternalFeedPage,
  LogsPage,
  SettingsPage 
} from './pages';

// Services
import { WebSocketService, ConstitutionalUpdate } from './services/WebSocketService';
import { APIService, ConstitutionalStatus, SystemHealth } from './services/APIService';

// Constitutional theme with privacy-first design
const constitutionalTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4CAF50', // Constitutional green
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#2196F3', // Trust blue
      contrastText: '#ffffff',
    },
    error: {
      main: '#F44336', // Violation red
    },
    warning: {
      main: '#FF9800', // Warning orange
    },
    info: {
      main: '#00BCD4', // Information cyan
    },
    success: {
      main: '#4CAF50', // Success green
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      color: '#4CAF50',
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          borderBottom: '1px solid #333',
        },
      },
    },
    MuiBottomNavigation: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          borderTop: '1px solid #333',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#2a2a2a',
          border: '1px solid #333',
        },
      },
    },
  },
});

const App: React.FC = () => {
  // Navigation state
  const [currentPage, setCurrentPage] = useState(0);
  
  // System state
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [constitutionalStatus, setConstitutionalStatus] = useState<ConstitutionalStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  // Alerts
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState<'success' | 'warning' | 'error' | 'info'>('info');

  // Services
  const [webSocketService] = useState(() => new WebSocketService());
  const [apiService] = useState(() => new APIService());

  // Page configuration with constitutional principles
  const pages = [
    {
      label: 'Chat',
      icon: <Chat />,
      component: <ChatPage apiService={apiService} />,
      description: 'Audio-visual chat with Admin AI'
    },
    {
      label: 'Network',
      icon: <AccountTree />,
      component: <NetworkVisualizationPage apiService={apiService} />,
      description: 'Decentralized network visualization'
    },
    {
      label: 'Feed',
      icon: <Timeline />,
      component: <InternalFeedPage webSocketService={webSocketService} />,
      description: 'Constitutional AI activity feed'
    },
    {
      label: 'Logs',
      icon: <Terminal />,
      component: <LogsPage apiService={apiService} />,
      description: 'System logs and audit trail'
    },
    {
      label: 'Settings',
      icon: <Settings />,
      component: <SettingsPage apiService={apiService} />,
      description: 'Constitutional settings and controls'
    }
  ];

  // Initialize services
  useEffect(() => {
    const initializeServices = async () => {
      try {
        // Initialize WebSocket connection
        webSocketService.connect();
        
        // Set up WebSocket event handlers
        webSocketService.onConnect(() => {
          setIsConnected(true);
          showAlert('Connected to HAI-Net Constitutional AI', 'success');
        });

        webSocketService.onDisconnect(() => {
          setIsConnected(false);
          showAlert('Disconnected from HAI-Net', 'warning');
        });

    webSocketService.onConstitutionalUpdate((update: ConstitutionalUpdate) => {
      // Convert ConstitutionalUpdate to ConstitutionalStatus format
      const constitutionalStatus: ConstitutionalStatus = {
        constitutional_status: {
          compliance_score: update.compliance_score,
          privacy_score: update.privacy_score,
          human_rights_score: update.human_rights_score,
          decentralization_score: update.decentralization_score,
          community_score: update.community_score,
          monitoring_active: update.monitoring_active,
          total_violations: 0,
          recent_violations: 0,
        },
        timestamp: Date.now(),
      };
      setConstitutionalStatus(constitutionalStatus);
      
      // Alert on compliance issues
      if (update.compliance_score < 0.8) {
        showAlert(`Constitutional compliance low: ${(update.compliance_score * 100).toFixed(1)}%`, 'warning');
      }
    });

        // Initial system health check
        const health = await apiService.getSystemHealth();
        setSystemHealth(health);

        // Initial constitutional status
        const constitutional = await apiService.getConstitutionalStatus();
        setConstitutionalStatus(constitutional);

        if (!health.constitutional_compliant) {
          showAlert('Constitutional compliance issues detected', 'error');
        }

      } catch (error) {
        console.error('Service initialization failed:', error);
        showAlert('Failed to initialize HAI-Net services', 'error');
      }
    };

    initializeServices();

    // Cleanup on unmount
    return () => {
      webSocketService.disconnect();
    };
  }, [webSocketService, apiService]);

  // Health check interval
  useEffect(() => {
    const healthCheckInterval = setInterval(async () => {
      try {
        const health = await apiService.getSystemHealth();
        setSystemHealth(health);
      } catch (error) {
        console.error('Health check failed:', error);
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(healthCheckInterval);
  }, [apiService]);

  const showAlert = (message: string, severity: 'success' | 'warning' | 'error' | 'info') => {
    setAlertMessage(message);
    setAlertSeverity(severity);
    setAlertOpen(true);
  };

  const handleCloseAlert = () => {
    setAlertOpen(false);
  };

  const getComplianceColor = (score: number): string => {
    if (score >= 0.9) return '#4CAF50'; // Green
    if (score >= 0.8) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const getConnectionStatus = (): { color: string; text: string } => {
    if (!isConnected) return { color: '#F44336', text: 'Disconnected' };
    if (!systemHealth?.constitutional_compliant) return { color: '#FF9800', text: 'Non-Compliant' };
    return { color: '#4CAF50', text: 'Constitutional' };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <ThemeProvider theme={constitutionalTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          {/* Constitutional Header */}
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <Security sx={{ mr: 2, color: '#4CAF50' }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                HAI-Net Constitutional AI
              </Typography>
              
              {/* Connection Status */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: connectionStatus.color,
                  }}
                />
                <Typography variant="body2" sx={{ color: connectionStatus.color }}>
                  {connectionStatus.text}
                </Typography>
              </Box>

              {/* Constitutional Compliance Score */}
              {constitutionalStatus && (
                <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: '#b3b3b3' }}>
                    Compliance:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      color: getComplianceColor(constitutionalStatus.constitutional_status.compliance_score),
                      fontWeight: 'bold'
                    }}
                  >
                    {(constitutionalStatus.constitutional_status.compliance_score * 100).toFixed(1)}%
                  </Typography>
                </Box>
              )}
            </Toolbar>
          </AppBar>

          {/* Main Content Area */}
          <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
            <Routes>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route path="/chat" element={pages[0].component} />
              <Route path="/network" element={pages[1].component} />
              <Route path="/feed" element={pages[2].component} />
              <Route path="/logs" element={pages[3].component} />
              <Route path="/settings" element={pages[4].component} />
            </Routes>
          </Box>

          {/* Constitutional Bottom Navigation */}
          <BottomNavigation
            value={currentPage}
            onChange={(event, newValue) => {
              setCurrentPage(newValue);
              // Navigate to corresponding route
              const routes = ['/chat', '/network', '/feed', '/logs', '/settings'];
              window.history.pushState(null, '', routes[newValue]);
            }}
            showLabels
          >
            {pages.map((page, index) => (
              <BottomNavigationAction
                key={index}
                label={page.label}
                icon={page.icon}
                sx={{
                  '&.Mui-selected': {
                    color: '#4CAF50',
                  },
                }}
              />
            ))}
          </BottomNavigation>

          {/* Constitutional Alerts */}
          <Snackbar
            open={alertOpen}
            autoHideDuration={6000}
            onClose={handleCloseAlert}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Alert 
              onClose={handleCloseAlert} 
              severity={alertSeverity}
              variant="filled"
              sx={{ width: '100%' }}
            >
              {alertMessage}
            </Alert>
          </Snackbar>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
