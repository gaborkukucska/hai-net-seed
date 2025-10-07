/**
 * HAI-Net Chat Page - Audio-Visual Interface with Session Management
 * Constitutional compliance: Privacy First + Human Rights
 * Main chat interface for interacting with Admin AI
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  List,
  ListItem,
  CircularProgress,
  Chip,
  Tooltip,
  Card,
  CardContent,
  Drawer,
  Divider,
  ListItemButton,
  ListItemText,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Send,
  Mic,
  MicOff,
  SmartToy,
  Person,
  Security,
  CheckCircle,
  Warning,
  History,
  Add,
  Delete,
  MoreVert,
} from '@mui/icons-material';
import { APIService, ChatMessage, ChatResponse } from '../services/APIService';
import { WebSocketService, AgentEvent } from '../services/WebSocketService';

interface ChatPageProps {
  apiService: APIService;
  websocketService?: WebSocketService;
}

interface DisplayMessage extends ChatMessage {
  id: string;
  isLoading?: boolean;
  constitutional_compliant?: boolean;
  privacy_protected?: boolean;
}

interface ChatSession {
  id: string;
  name: string;
  createdAt: number;
  lastActiveAt: number;
  messages: DisplayMessage[];
}

const SESSIONS_STORAGE_KEY = 'hainet_chat_sessions';
const ACTIVE_SESSION_KEY = 'hainet_active_session_id';

export const ChatPage: React.FC<ChatPageProps> = ({ apiService, websocketService }) => {
  // Session management
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [sessionDrawerOpen, setSessionDrawerOpen] = useState(false);
  const [sessionMenuAnchor, setSessionMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedSessionForMenu, setSelectedSessionForMenu] = useState<string>('');

  // Chat state
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Load sessions from localStorage
  const loadSessions = () => {
    try {
      const storedSessions = localStorage.getItem(SESSIONS_STORAGE_KEY);
      const storedActiveId = localStorage.getItem(ACTIVE_SESSION_KEY);
      
      if (storedSessions) {
        const parsedSessions: ChatSession[] = JSON.parse(storedSessions);
        setSessions(parsedSessions);
        
        // Load active session or create new one
        if (storedActiveId && parsedSessions.some(s => s.id === storedActiveId)) {
          loadSession(storedActiveId, parsedSessions);
        } else {
          createNewSession(parsedSessions);
        }
      } else {
        // First time - create initial session
        createNewSession([]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      createNewSession([]);
    }
  };

  // Save sessions to localStorage
  const saveSessions = (sessionsToSave: ChatSession[], activeId: string) => {
    try {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessionsToSave));
      localStorage.setItem(ACTIVE_SESSION_KEY, activeId);
    } catch (error) {
      console.error('Failed to save sessions:', error);
    }
  };

  // Create a new session
  const createNewSession = (existingSessions: ChatSession[]) => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      name: `Session ${new Date().toLocaleString()}`,
      createdAt: Date.now(),
      lastActiveAt: Date.now(),
      messages: [
        {
          id: '0',
          role: 'assistant',
          content: '👋 Hello! I\'m your HAI-Net Admin AI entity. I\'m here to help you with your professional and personal goals while maintaining constitutional compliance. How can I assist you today?',
          timestamp: Date.now(),
          constitutional_compliant: true,
          privacy_protected: true,
        },
      ],
    };

    const updatedSessions = [newSession, ...existingSessions];
    setSessions(updatedSessions);
    setActiveSessionId(newSession.id);
    setMessages(newSession.messages);
    saveSessions(updatedSessions, newSession.id);
  };

  // Load a specific session
  const loadSession = (sessionId: string, sessionsToSearch?: ChatSession[]) => {
    const sessionList = sessionsToSearch || sessions;
    const session = sessionList.find(s => s.id === sessionId);
    
    if (session) {
      setActiveSessionId(session.id);
      setMessages(session.messages);
      
      // Update last active time
      const updatedSessions = sessionList.map(s =>
        s.id === sessionId ? { ...s, lastActiveAt: Date.now() } : s
      );
      setSessions(updatedSessions);
      saveSessions(updatedSessions, sessionId);
    }
  };

  // Update current session messages (filter out loading messages before saving)
  useEffect(() => {
    if (activeSessionId && messages.length > 0) {
      // Don't persist thinking/loading messages to session storage
      const messagesToSave = messages.filter(msg => !msg.isLoading);
      
      const updatedSessions = sessions.map(s =>
        s.id === activeSessionId
          ? { ...s, messages: messagesToSave, lastActiveAt: Date.now() }
          : s
      );
      setSessions(updatedSessions);
      saveSessions(updatedSessions, activeSessionId);
    }
  }, [messages]);

  // Delete a session
  const deleteSession = (sessionId: string) => {
    const updatedSessions = sessions.filter(s => s.id !== sessionId);
    
    // If deleting active session, switch to another or create new
    if (sessionId === activeSessionId) {
      if (updatedSessions.length > 0) {
        loadSession(updatedSessions[0].id, updatedSessions);
      } else {
        createNewSession([]);
      }
    } else {
      setSessions(updatedSessions);
      saveSessions(updatedSessions, activeSessionId);
    }
  };

  // Handle session menu
  const handleSessionMenuOpen = (event: React.MouseEvent<HTMLElement>, sessionId: string) => {
    setSessionMenuAnchor(event.currentTarget);
    setSelectedSessionForMenu(sessionId);
  };

  const handleSessionMenuClose = () => {
    setSessionMenuAnchor(null);
    setSelectedSessionForMenu('');
  };

  const handleDeleteSession = () => {
    if (selectedSessionForMenu) {
      deleteSession(selectedSessionForMenu);
    }
    handleSessionMenuClose();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize WebSocket connection and event handlers
  useEffect(() => {
    if (!websocketService) return;

    // Connect WebSocket
    websocketService.connect();

    // Subscribe to agent events for streaming
    websocketService.onAgentEvent((event: AgentEvent) => {
      console.log('Received agent event:', event);

      switch (event.event) {
        case 'agent_thinking':
          // Show thinking indicator
          const thinkingId = `${event.agent_id}-thinking-${event.timestamp}`;
          setStreamingMessageId(thinkingId);
          setMessages((prev) => [
            ...prev,
            {
              id: thinkingId,
              role: 'assistant',
              content: event.thought || 'Thinking...',
              timestamp: event.timestamp,
              isLoading: true,
            },
          ]);
          break;

        case 'response_chunk':
          // Accumulate chunks into streaming message
          if (event.chunk) {
            setMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.isLoading) {
                // Update existing streaming message
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    content: (lastMessage.content || '') + event.chunk,
                    isLoading: true,
                  },
                ];
              } else {
                // Create new streaming message if none exists
                const newId = `${event.agent_id}-stream-${event.timestamp}`;
                setStreamingMessageId(newId);
                return [
                  ...prev,
                  {
                    id: newId,
                    role: 'assistant',
                    content: event.chunk,
                    timestamp: event.timestamp,
                    isLoading: true,
                  },
                ];
              }
            });
          }
          break;

        case 'response_complete':
          // Finalize streaming message
          setMessages((prev) => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.isLoading) {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMessage,
                  content: event.response || lastMessage.content,
                  isLoading: false,
                  constitutional_compliant: true,
                  privacy_protected: true,
                },
              ];
            }
            return prev;
          });
          setStreamingMessageId(null);
          setIsLoading(false);
          break;

        case 'tool_execution_start':
          // Show tool execution indicator
          setMessages((prev) => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.isLoading) {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMessage,
                  content: `🔧 Executing tool: ${event.role || 'unknown'}...`,
                },
              ];
            }
            return prev;
          });
          break;

        case 'tool_execution_complete':
          // Tool execution complete - continue streaming
          break;

        case 'error':
          // Handle error events
          setMessages((prev) => {
            const filtered = prev.filter((msg) => !msg.isLoading);
            return [
              ...filtered,
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: `⚠️ Error: ${event.chunk || 'Unknown error occurred'}`,
                timestamp: event.timestamp,
                constitutional_compliant: false,
              },
            ];
          });
          setStreamingMessageId(null);
          setIsLoading(false);
          break;
      }
    });

    // Cleanup on unmount - don't disconnect WebSocket as it's managed at App level
    return () => {
      // WebSocket cleanup is handled by App.tsx
    };
  }, [websocketService]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: DisplayMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Add loading message
      const loadingMessage: DisplayMessage = {
        id: `${Date.now()}-loading`,
        role: 'assistant',
        content: '',
        isLoading: true,
      };
      setMessages((prev) => [...prev, loadingMessage]);

      // Send to API
      const response: ChatResponse = await apiService.chatWithAI(
        messages.map((msg) => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
        })).concat([{ role: 'user', content: inputMessage, timestamp: Date.now() }]),
        '', // Let backend choose model
        undefined // No user DID yet
      );

      // Remove loading message and add actual response
      setMessages((prev) => {
        const filtered = prev.filter((msg) => msg.id !== loadingMessage.id);
        return [
          ...filtered,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: response.response,
            timestamp: response.timestamp,
            constitutional_compliant: response.constitutional_compliant,
            privacy_protected: response.privacy_protected,
          },
        ];
      });
    } catch (error) {
      console.error('Chat error:', error);
      
      // Remove loading message
      setMessages((prev) => prev.filter((msg) => !msg.isLoading));
      
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: `⚠️ I apologize, but I encountered an error: ${error}. This might be because the LLM service is not yet available. Please ensure Ollama or another LLM provider is running.`,
          timestamp: Date.now(),
          constitutional_compliant: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const toggleVoiceInput = () => {
    // TODO: Implement voice input with Web Speech API
    setIsListening(!isListening);
    if (!isListening) {
      // Start listening
      console.log('Voice input not yet implemented');
    } else {
      // Stop listening
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#121212',
      }}
    >
      {/* Chat Header */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          backgroundColor: '#1e1e1e',
          borderBottom: '1px solid #333',
          borderRadius: 0,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: '#4CAF50' }}>
            <SmartToy />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ color: '#4CAF50' }}>
              Admin AI Entity
            </Typography>
            <Typography variant="caption" sx={{ color: '#b3b3b3' }}>
              Constitutional AI • Privacy First • Local Processing
            </Typography>
          </Box>
          
          {/* Session Controls */}
          <Tooltip title="New Session">
            <IconButton
              onClick={() => createNewSession(sessions)}
              sx={{ color: '#4CAF50' }}
            >
              <Add />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Session History">
            <IconButton
              onClick={() => setSessionDrawerOpen(true)}
              sx={{ color: '#4CAF50' }}
            >
              <History />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Constitutional Compliance">
            <Security sx={{ color: '#4CAF50' }} />
          </Tooltip>
        </Box>
      </Paper>

      {/* Session Drawer */}
      <Drawer
        anchor="right"
        open={sessionDrawerOpen}
        onClose={() => setSessionDrawerOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: 320,
            backgroundColor: '#1e1e1e',
            color: '#ffffff',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ color: '#4CAF50', mb: 2 }}>
            Chat Sessions
          </Typography>
          
          <Button
            fullWidth
            startIcon={<Add />}
            variant="contained"
            onClick={() => {
              createNewSession(sessions);
              setSessionDrawerOpen(false);
            }}
            sx={{
              mb: 2,
              bgcolor: '#4CAF50',
              '&:hover': { bgcolor: '#45a049' },
            }}
          >
            New Session
          </Button>
          
          <Divider sx={{ borderColor: '#333', mb: 2 }} />
          
          <List sx={{ p: 0 }}>
            {sessions.map((session) => (
              <ListItemButton
                key={session.id}
                selected={session.id === activeSessionId}
                onClick={() => {
                  loadSession(session.id);
                  setSessionDrawerOpen(false);
                }}
                sx={{
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: session.id === activeSessionId ? '#2a2a2a' : 'transparent',
                  '&:hover': { backgroundColor: '#333' },
                  '&.Mui-selected': {
                    backgroundColor: '#2a2a2a',
                    borderLeft: '3px solid #4CAF50',
                  },
                }}
              >
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ color: '#ffffff' }}>
                      {new Date(session.createdAt).toLocaleDateString()}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" sx={{ color: '#b3b3b3' }}>
                      {new Date(session.createdAt).toLocaleTimeString()} • {session.messages.length} messages
                    </Typography>
                  }
                />
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSessionMenuOpen(e, session.id);
                  }}
                  sx={{ color: '#b3b3b3' }}
                >
                  <MoreVert fontSize="small" />
                </IconButton>
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Session Menu */}
      <Menu
        anchorEl={sessionMenuAnchor}
        open={Boolean(sessionMenuAnchor)}
        onClose={handleSessionMenuClose}
        PaperProps={{
          sx: {
            backgroundColor: '#2a2a2a',
            color: '#ffffff',
          },
        }}
      >
        <MenuItem
          onClick={handleDeleteSession}
          disabled={sessions.length <= 1}
          sx={{ color: '#F44336' }}
        >
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete Session
        </MenuItem>
      </Menu>

      {/* Messages Area */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          backgroundColor: '#121212',
        }}
      >
        <List>
          {messages.map((message) => (
            <ListItem
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
                px: 0,
              }}
            >
              <Card
                sx={{
                  maxWidth: '70%',
                  backgroundColor: message.role === 'user' ? '#2196F3' : '#2a2a2a',
                  border: message.role === 'assistant' ? '1px solid #333' : 'none',
                }}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  {/* Message Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Avatar
                      sx={{
                        width: 24,
                        height: 24,
                        bgcolor: message.role === 'user' ? '#1976D2' : '#4CAF50',
                      }}
                    >
                      {message.role === 'user' ? (
                        <Person sx={{ fontSize: 16 }} />
                      ) : (
                        <SmartToy sx={{ fontSize: 16 }} />
                      )}
                    </Avatar>
                    <Typography variant="caption" sx={{ color: '#b3b3b3', fontWeight: 500 }}>
                      {message.role === 'user' ? 'You' : 'Admin AI'}
                    </Typography>
                    
                    {/* Constitutional Compliance Indicators */}
                    {message.role === 'assistant' && message.constitutional_compliant && (
                      <Tooltip title="Constitutional Compliant">
                        <CheckCircle sx={{ fontSize: 16, color: '#4CAF50' }} />
                      </Tooltip>
                    )}
                    {message.role === 'assistant' && message.privacy_protected && (
                      <Tooltip title="Privacy Protected">
                        <Security sx={{ fontSize: 16, color: '#4CAF50' }} />
                      </Tooltip>
                    )}
                    {message.role === 'assistant' && message.constitutional_compliant === false && (
                      <Tooltip title="Constitutional Compliance Warning">
                        <Warning sx={{ fontSize: 16, color: '#FF9800' }} />
                      </Tooltip>
                    )}
                  </Box>

                  {/* Message Content */}
                  {message.isLoading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} sx={{ color: '#4CAF50' }} />
                      <Typography variant="body2" sx={{ color: '#b3b3b3' }}>
                        Thinking...
                      </Typography>
                    </Box>
                  ) : (
                    <Typography
                      variant="body1"
                      sx={{
                        color: '#ffffff',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {message.content}
                    </Typography>
                  )}

                  {/* Timestamp */}
                  {message.timestamp && (
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 1,
                        color: '#666',
                        textAlign: message.role === 'user' ? 'right' : 'left',
                      }}
                    >
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      {/* Input Area */}
      <Paper
        elevation={3}
        sx={{
          p: 2,
          backgroundColor: '#1e1e1e',
          borderTop: '1px solid #333',
          borderRadius: 0,
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          {/* Voice Input Button */}
          <Tooltip title={isListening ? 'Stop listening' : 'Voice input (coming soon)'}>
            <IconButton
              onClick={toggleVoiceInput}
              sx={{
                color: isListening ? '#F44336' : '#b3b3b3',
                '&:hover': { backgroundColor: '#333' },
              }}
              disabled
            >
              {isListening ? <Mic /> : <MicOff />}
            </IconButton>
          </Tooltip>

          {/* Text Input */}
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message to Admin AI..."
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#2a2a2a',
                color: '#ffffff',
                '& fieldset': {
                  borderColor: '#333',
                },
                '&:hover fieldset': {
                  borderColor: '#4CAF50',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#4CAF50',
                },
              },
              '& .MuiInputBase-input::placeholder': {
                color: '#666',
                opacity: 1,
              },
            }}
          />

          {/* Send Button */}
          <Tooltip title="Send message">
            <span>
              <IconButton
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                sx={{
                  bgcolor: '#4CAF50',
                  color: '#ffffff',
                  '&:hover': {
                    bgcolor: '#45a049',
                  },
                  '&.Mui-disabled': {
                    bgcolor: '#333',
                    color: '#666',
                  },
                }}
              >
                {isLoading ? <CircularProgress size={24} sx={{ color: '#666' }} /> : <Send />}
              </IconButton>
            </span>
          </Tooltip>
        </Box>

        {/* Status Indicators */}
        <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          <Chip
            icon={<Security />}
            label="Privacy Protected"
            size="small"
            sx={{ bgcolor: '#2a2a2a', color: '#4CAF50', borderColor: '#4CAF50', border: '1px solid' }}
            variant="outlined"
          />
          <Chip
            icon={<CheckCircle />}
            label="Local Processing"
            size="small"
            sx={{ bgcolor: '#2a2a2a', color: '#4CAF50', borderColor: '#4CAF50', border: '1px solid' }}
            variant="outlined"
          />
          <Typography variant="caption" sx={{ color: '#666', ml: 'auto' }}>
            Session: {new Date(sessions.find(s => s.id === activeSessionId)?.createdAt || Date.now()).toLocaleString()}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatPage;
