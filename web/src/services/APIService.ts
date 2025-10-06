// START OF FILE web/src/services/APIService.ts
/**
 * HAI-Net API Service
 * Constitutional compliance: Privacy First + Local processing
 * Service for communicating with HAI-Net FastAPI backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

export interface SystemHealth {
  status: string;
  constitutional_compliant: boolean;
  version: string;
  timestamp: number;
}

export interface ConstitutionalStatus {
  constitutional_status: {
    compliance_score: number;
    privacy_score: number;
    human_rights_score: number;
    decentralization_score: number;
    community_score: number;
    monitoring_active: boolean;
    total_violations: number;
    recent_violations: number;
  };
  timestamp: number;
}

export interface Agent {
  agent_id: string;
  role: string;
  current_state: string;
  capabilities: string[];
  health_score: number;
  uptime: number;
  constitutional_compliant: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
}

export interface ChatResponse {
  response: string;
  model: string;
  constitutional_compliant: boolean;
  privacy_protected: boolean;
  timestamp: number;
}

export interface NetworkStatus {
  status: string;
  connected_peers: number;
  discovery_active: boolean;
  constitutional_compliant: boolean;
}

export interface Settings {
  constitutional_version: string;
  privacy_mode: boolean;
  local_processing: boolean;
  decentralized: boolean;
  community_focused: boolean;
}

export class APIService {
  private api: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.api = axios.create({
      baseURL,
      timeout: 150000, // 150 seconds - allows time for LLM model loading
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for constitutional compliance logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`HAI-Net API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('HAI-Net API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        console.error('HAI-Net API Response Error:', error);
        throw new Error(`API Error: ${error.response?.data?.detail || error.message}`);
      }
    );
  }

  /**
   * Get system health status
   */
  async getSystemHealth(): Promise<SystemHealth> {
    try {
      const response: AxiosResponse<SystemHealth> = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get system health: ${error}`);
    }
  }

  /**
   * Get constitutional compliance status
   */
  async getConstitutionalStatus(): Promise<ConstitutionalStatus> {
    try {
      const response: AxiosResponse<ConstitutionalStatus> = await this.api.get('/constitutional/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get constitutional status: ${error}`);
    }
  }

  /**
   * Get all agents
   */
  async getAgents(): Promise<Agent[]> {
    try {
      const response: AxiosResponse<{ agents: Agent[] }> = await this.api.get('/agents');
      return response.data.agents;
    } catch (error) {
      throw new Error(`Failed to get agents: ${error}`);
    }
  }

  /**
   * Create a new agent
   */
  async createAgent(role: string, userDid?: string): Promise<string> {
    try {
      const response: AxiosResponse<{ success: boolean; agent_id: string }> = await this.api.post('/agents/create', {
        role,
        user_did: userDid,
      });
      
      if (response.data.success) {
        return response.data.agent_id;
      } else {
        throw new Error('Agent creation failed');
      }
    } catch (error) {
      throw new Error(`Failed to create agent: ${error}`);
    }
  }

  /**
   * Chat with AI
   */
  async chatWithAI(messages: ChatMessage[], model: string, userDid?: string): Promise<ChatResponse> {
    try {
      const response: AxiosResponse<ChatResponse> = await this.api.post('/chat', {
        messages,
        model,
        user_did: userDid,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to chat with AI: ${error}`);
    }
  }

  /**
   * Get network status
   */
  async getNetworkStatus(): Promise<NetworkStatus> {
    try {
      const response: AxiosResponse<NetworkStatus> = await this.api.get('/network/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get network status: ${error}`);
    }
  }

  /**
   * Get agent memory summary
   */
  async getAgentMemory(agentId: string): Promise<any> {
    try {
      const response: AxiosResponse<{ memory_summary: any }> = await this.api.get(`/memory/${agentId}`);
      return response.data.memory_summary;
    } catch (error) {
      throw new Error(`Failed to get agent memory: ${error}`);
    }
  }

  /**
   * Search agent memory
   */
  async searchAgentMemory(agentId: string, query: string, limit: number = 10): Promise<any[]> {
    try {
      const response: AxiosResponse<{ results: any[] }> = await this.api.post(`/memory/${agentId}/search`, {
        query,
        limit,
      });
      return response.data.results;
    } catch (error) {
      throw new Error(`Failed to search agent memory: ${error}`);
    }
  }

  /**
   * Get settings
   */
  async getSettings(): Promise<Settings> {
    try {
      const response: AxiosResponse<Settings> = await this.api.get('/settings');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get settings: ${error}`);
    }
  }

  /**
   * Get logs (simulated - would integrate with actual logging endpoint)
   */
  async getLogs(limit: number = 100): Promise<any[]> {
    // This would integrate with actual logging endpoint
    // For now, return simulated logs
    return [
      {
        timestamp: Date.now(),
        level: 'INFO',
        component: 'constitutional_guardian',
        message: 'Constitutional monitoring active',
        constitutional_compliant: true,
      },
      {
        timestamp: Date.now() - 1000,
        level: 'INFO',
        component: 'agent_manager',
        message: 'Agent created successfully',
        constitutional_compliant: true,
      },
      {
        timestamp: Date.now() - 2000,
        level: 'INFO',
        component: 'web_server',
        message: 'Client connected via WebSocket',
        constitutional_compliant: true,
      },
    ];
  }
}

export default APIService;
