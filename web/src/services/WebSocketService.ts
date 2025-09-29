// START OF FILE web/src/services/WebSocketService.ts
/**
 * HAI-Net WebSocket Service
 * Constitutional compliance: Privacy First + Real-time communication
 * Service for real-time communication with HAI-Net backend
 */

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: number;
}

export interface ConstitutionalUpdate {
  compliance_score: number;
  privacy_score: number;
  human_rights_score: number;
  decentralization_score: number;
  community_score: number;
  monitoring_active: boolean;
}

export interface AgentUpdate {
  agent_id: string;
  state: string;
  health_score: number;
  constitutional_compliant: boolean;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;
  private clientId: string;
  
  // Event handlers
  private onConnectHandler: (() => void) | null = null;
  private onDisconnectHandler: (() => void) | null = null;
  private onConstitutionalUpdateHandler: ((status: ConstitutionalUpdate) => void) | null = null;
  private onAgentUpdateHandler: ((update: AgentUpdate) => void) | null = null;
  private onMessageHandler: ((message: WebSocketMessage) => void) | null = null;

  constructor() {
    this.clientId = this.generateClientId();
  }

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('HAI-Net WebSocket connected');
        this.reconnectAttempts = 0;
        
        if (this.onConnectHandler) {
          this.onConnectHandler();
        }

        // Send initial ping
        this.send({
          type: 'ping',
          timestamp: Date.now(),
        });

        // Subscribe to constitutional updates
        this.send({
          type: 'subscribe_constitutional_updates',
        });

        // Subscribe to agent updates
        this.send({
          type: 'subscribe_agent_updates',
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('HAI-Net WebSocket disconnected');
        this.ws = null;
        
        if (this.onDisconnectHandler) {
          this.onDisconnectHandler();
        }

        // Attempt to reconnect
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('HAI-Net WebSocket error:', error);
      };

    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send message to server
   */
  public send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: message.timestamp || Date.now(),
      }));
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'pong':
        // Handle pong response
        break;

      case 'constitutional_update':
        if (this.onConstitutionalUpdateHandler && message.data) {
          this.onConstitutionalUpdateHandler(message.data as ConstitutionalUpdate);
        }
        break;

      case 'agent_update':
        if (this.onAgentUpdateHandler && message.data) {
          this.onAgentUpdateHandler(message.data as AgentUpdate);
        }
        break;

      case 'subscription_confirmed':
        console.log(`Subscribed to: ${message.data?.subscription}`);
        break;

      default:
        if (this.onMessageHandler) {
          this.onMessageHandler(message);
        }
        break;
    }
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  /**
   * Set connect handler
   */
  public onConnect(handler: () => void): void {
    this.onConnectHandler = handler;
  }

  /**
   * Set disconnect handler
   */
  public onDisconnect(handler: () => void): void {
    this.onDisconnectHandler = handler;
  }

  /**
   * Set constitutional update handler
   */
  public onConstitutionalUpdate(handler: (status: ConstitutionalUpdate) => void): void {
    this.onConstitutionalUpdateHandler = handler;
  }

  /**
   * Set agent update handler
   */
  public onAgentUpdate(handler: (update: AgentUpdate) => void): void {
    this.onAgentUpdateHandler = handler;
  }

  /**
   * Set generic message handler
   */
  public onMessage(handler: (message: WebSocketMessage) => void): void {
    this.onMessageHandler = handler;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  public getConnectionState(): string {
    if (!this.ws) return 'CLOSED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }
}

export default WebSocketService;
