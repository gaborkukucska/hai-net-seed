/**
 * HAI-Net Chat Page - Audio-Visual Interface
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
} from '@mui/icons-material';
import { APIService, ChatMessage, ChatResponse } from '../services/APIService';

interface ChatPageProps {
  apiService: APIService;
}

interface DisplayMessage extends ChatMessage {
  id: string;
  isLoading?: boolean;
  constitutional_compliant?: boolean;
  privacy_protected?: boolean;
}

export const ChatPage: React.FC<ChatPageProps> = ({ apiService }) => {
  const [messages, setMessages] = useState<DisplayMessage[]>([
    {
      id: '0',
      role: 'assistant',
      content: '👋 Hello! I\'m your HAI-Net Admin AI entity. I\'m here to help you with your professional and personal goals while maintaining constitutional compliance. How can I assist you today?',
      timestamp: Date.now(),
      constitutional_compliant: true,
      privacy_protected: true,
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          <Tooltip title="Constitutional Compliance">
            <Security sx={{ color: '#4CAF50' }} />
          </Tooltip>
        </Box>
      </Paper>

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
        <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
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
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatPage;
