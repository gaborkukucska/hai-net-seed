<!-- # START OF FILE helperfiles/FUNCTIONS_INDEX.MD -->
# Functions Index (v0.02)

This file tracks the core functions/methods defined within the framework, categorized by component. It helps in understanding the codebase and navigating between different parts.

*   **Format:** `[File Path]::[Class Name]::[Method Name](parameters) - Description` or `[File Path]::[Function Name](parameters) - Description`

---

## Identity Management System

### core/identity/did.py

**Classes:**
- `[core/identity/did.py]::[ConstitutionalViolationError] - Exception for constitutional principle violations`
- `[core/identity/did.py]::[DIDGenerator] - Generates deterministic DIDs using Argon2id`
- `[core/identity/did.py]::[IdentityManager] - Manages user identity and cryptographic operations`

**DIDGenerator Methods:**
- `[core/identity/did.py]::[DIDGenerator]::[__init__]() - Initialize DID generator with Argon2 configuration`
- `[core/identity/did.py]::[DIDGenerator]::[generate_did](full_name, date_of_birth, government_id, passphrase) - Generate deterministic DID from personal information`
- `[core/identity/did.py]::[DIDGenerator]::[_validate_inputs](full_name, date_of_birth, government_id, passphrase) - Validate inputs for constitutional compliance`

**IdentityManager Methods:**
- `[core/identity/did.py]::[IdentityManager]::[__init__]() - Initialize identity manager`
- `[core/identity/did.py]::[IdentityManager]::[create_identity](full_name, date_of_birth, government_id, passphrase, email) - Create comprehensive user identity`
- `[core/identity/did.py]::[IdentityManager]::[load_identity](did, passphrase) - Load existing identity with verification`
- `[core/identity/did.py]::[IdentityManager]::[watermark_data](data, content_type) - Add constitutional watermark to AI content`
- `[core/identity/did.py]::[IdentityManager]::[verify_watermark](data) - Verify and extract watermark from content`

**Utility Functions:**
- `[core/identity/did.py]::[create_test_identity]() - Create test identity for development`

---

## Configuration Management System

### core/config/settings.py

**Classes:**
- `[core/config/settings.py]::[HAINetSettings] - Main configuration settings with constitutional compliance`
- `[core/config/settings.py]::[DevelopmentSettings] - Development-specific settings`
- `[core/config/settings.py]::[ProductionSettings] - Production-specific settings`

**HAINetSettings Methods:**
- `[core/config/settings.py]::[HAINetSettings]::[constitutional_compliance_check]() - Verify settings comply with constitutional principles`
- `[core/config/settings.py]::[HAINetSettings]::[get_secure_config]() - Get configuration with sensitive data removed`

**Utility Functions:**
- `[core/config/settings.py]::[get_settings](environment) - Get appropriate settings for environment`
- `[core/config/settings.py]::[validate_constitutional_compliance](settings) - Validate constitutional compliance`

### core/config/config_manager.py

**Classes:**
- `[core/config/config_manager.py]::[ConfigManager] - Manages configuration with constitutional compliance`

**ConfigManager Methods:**
- `[core/config/config_manager.py]::[ConfigManager]::[__init__](config_dir) - Initialize configuration manager`
- `[core/config/config_manager.py]::[ConfigManager]::[_initialize_config]() - Initialize configuration with constitutional compliance`
- `[core/config/config_manager.py]::[ConfigManager]::[load_config](environment) - Load configuration with constitutional validation`
- `[core/config/config_manager.py]::[ConfigManager]::[save_config]() - Save configuration with constitutional protection`
- `[core/config/config_manager.py]::[ConfigManager]::[update_setting](key, value) - Update setting with constitutional validation`
- `[core/config/config_manager.py]::[ConfigManager]::[get_setting](key, default) - Get setting value with default fallback`
- `[core/config/config_manager.py]::[ConfigManager]::[enable_resource_sharing](user_consent) - Enable resource sharing with user consent`
- `[core/config/config_manager.py]::[ConfigManager]::[configure_guardian_mode](mode) - Configure constitutional guardian mode`
- `[core/config/config_manager.py]::[ConfigManager]::[setup_local_hub](hub_name, node_role) - Setup local hub configuration`
- `[core/config/config_manager.py]::[ConfigManager]::[get_constitutional_status]() - Get constitutional compliance status`
- `[core/config/config_manager.py]::[ConfigManager]::[export_config](export_path, include_sensitive) - Export configuration to file`
- `[core/config/config_manager.py]::[ConfigManager]::[reset_to_defaults](environment) - Reset configuration to defaults`
- `[core/config/config_manager.py]::[ConfigManager]::[_log_config_change](message) - Log configuration changes for audit trail`
- `[core/config/config_manager.py]::[ConfigManager]::[_get_config_timestamp]() - Get current timestamp for configuration tracking`
- `[core/config/config_manager.py]::[ConfigManager]::[validate_current_config]() - Validate current configuration`

---

## Logging System

### core/logging/logger.py

**Classes:**
- `[core/logging/logger.py]::[HAINetLogger] - Constitutional compliance-aware logger`
- `[core/logging/logger.py]::[ConstitutionalLogFilter] - Filter to add constitutional context to log records`
- `[core/logging/logger.py]::[ConstitutionalFormatter] - Formatter with constitutional compliance information`

**HAINetLogger Methods:**
- `[core/logging/logger.py]::[HAINetLogger]::[__init__](name, settings) - Initialize constitutional logger with categorized debug support`
- `[core/logging/logger.py]::[HAINetLogger]::[log_constitutional_event](event_type, details, level) - Log constitutional compliance event`
- `[core/logging/logger.py]::[HAINetLogger]::[log_privacy_event](action, data_type, user_consent) - Log privacy-related events`
- `[core/logging/logger.py]::[HAINetLogger]::[log_human_rights_event](action, user_control) - Log human rights protection events`
- `[core/logging/logger.py]::[HAINetLogger]::[log_decentralization_event](action, local_processing) - Log decentralization events`
- `[core/logging/logger.py]::[HAINetLogger]::[log_community_event](action, community_benefit) - Log community focus events`
- `[core/logging/logger.py]::[HAINetLogger]::[log_violation](violation_type, details, severity) - Log constitutional violations`
- `[core/logging/logger.py]::[HAINetLogger]::[log_correction](correction_type, original_action, corrected_action) - Log constitutional corrections`
- `[core/logging/logger.py]::[HAINetLogger]::[get_compliance_summary]() - Get constitutional compliance summary`
- `[core/logging/logger.py]::[HAINetLogger]::[info](message, category, function) - Info level logging with categorization`
- `[core/logging/logger.py]::[HAINetLogger]::[debug](message, category, function) - Debug level logging with categorization`
- `[core/logging/logger.py]::[HAINetLogger]::[warning](message, category, function) - Warning level logging with categorization`
- `[core/logging/logger.py]::[HAINetLogger]::[error](message, category, function) - Error level logging with categorization`
- `[core/logging/logger.py]::[HAINetLogger]::[critical](message, category, function) - Critical level logging with categorization`

**Enhanced Categorized Logging Methods:**
- `[core/logging/logger.py]::[HAINetLogger]::[debug_init](message, function) - Debug initialization processes`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_network](message, function) - Debug network operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_crypto](message, function) - Debug cryptographic operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_ai](message, function) - Debug AI operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_storage](message, function) - Debug storage operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_web](message, function) - Debug web server operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_agent](message, function) - Debug agent operations`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_constitutional](message, function) - Debug constitutional compliance`
- `[core/logging/logger.py]::[HAINetLogger]::[debug_performance](message, function) - Debug performance metrics`
- `[core/logging/logger.py]::[HAINetLogger]::[info_init](message, function) - Info initialization processes`
- `[core/logging/logger.py]::[HAINetLogger]::[info_network](message, function) - Info network operations`
- `[core/logging/logger.py]::[HAINetLogger]::[info_web](message, function) - Info web server operations`
- `[core/logging/logger.py]::[HAINetLogger]::[warning_constitutional](message, function) - Warning for constitutional issues`
- `[core/logging/logger.py]::[HAINetLogger]::[warning_network](message, function) - Warning for network issues`
- `[core/logging/logger.py]::[HAINetLogger]::[error_constitutional](message, function) - Error for constitutional violations`

**Utility Functions:**
- `[core/logging/logger.py]::[get_logger](name, settings) - Get or create constitutional logger`
- `[core/logging/logger.py]::[log_system_start](component, version) - Log system component startup`

---

## Testing Framework

### tests/test_constitutional_compliance.py

**Test Classes:**
- `[tests/test_constitutional_compliance.py]::[TestPrivacyFirstPrinciple] - Test Article I compliance`
- `[tests/test_constitutional_compliance.py]::[TestHumanRightsProtection] - Test Article II compliance`
- `[tests/test_constitutional_compliance.py]::[TestDecentralizationImperative] - Test Article III compliance`
- `[tests/test_constitutional_compliance.py]::[TestCommunityFocusPrinciple] - Test Article IV compliance`

**Test Functions:**
- `[tests/test_constitutional_compliance.py]::[test_full_constitutional_compliance]() - Integration test for all constitutional principles`

---

## Networking System

### core/network/discovery.py

**Classes:**
- `[core/network/discovery.py]::[NetworkNode] - Represents a discovered HAI-Net node with trust metrics`
- `[core/network/discovery.py]::[ConstitutionalNetworkListener] - Service listener enforcing constitutional compliance`
- `[core/network/discovery.py]::[LocalDiscovery] - mDNS-based local network discovery for HAI-Net nodes`

**LocalDiscovery Methods:**
- `[core/network/discovery.py]::[LocalDiscovery]::[__init__](settings, node_id, did) - Initialize discovery service`
- `[core/network/discovery.py]::[LocalDiscovery]::[start_discovery]() - Start mDNS discovery service`
- `[core/network/discovery.py]::[LocalDiscovery]::[stop_discovery]() - Stop discovery service`
- `[core/network/discovery.py]::[LocalDiscovery]::[get_discovered_nodes](trusted_only) - Get list of discovered nodes`
- `[core/network/discovery.py]::[LocalDiscovery]::[get_node_by_id](node_id) - Get specific node by ID`
- `[core/network/discovery.py]::[LocalDiscovery]::[add_discovery_callback](callback) - Add callback for node discovery events`
- `[core/network/discovery.py]::[LocalDiscovery]::[add_removal_callback](callback) - Add callback for node removal events`
- `[core/network/discovery.py]::[LocalDiscovery]::[get_discovery_stats]() - Get discovery statistics`

**Utility Functions:**
- `[core/network/discovery.py]::[create_discovery_service](settings, node_id, did) - Create constitutional discovery service`

### core/network/llm_discovery.py - **🧠 NEW: Network-Wide AI Discovery System**

**Classes:**
- `[core/network/llm_discovery.py]::[LLMNode] - Represents discovered AI service providers with constitutional compliance`
- `[core/network/llm_discovery.py]::[ConstitutionalLLMListener] - mDNS listener for AI services with constitutional validation`
- `[core/network/llm_discovery.py]::[LLMDiscovery] - **MAJOR**: Comprehensive AI service discovery across local networks`

**LLMDiscovery Methods:**
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[__init__](settings, node_id) - Initialize AI discovery service`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[start_discovery]() - **NEW**: Start comprehensive AI discovery with mDNS + network scanning`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[stop_discovery]() - **NEW**: Graceful shutdown of all discovery services`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_start_network_scanning]() - **NEW**: Scans 800+ IPs across multiple network ranges`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_priority_scan_ollama](network_ranges) - **NEW**: High-speed priority scanning for Ollama services`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_get_comprehensive_network_ranges]() - **NEW**: Advanced network topology detection`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_scan_ai_service](ip, port, service_name) - **NEW**: Individual AI service scanning and validation`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_probe_ai_service](ip, port, service_name) - **NEW**: AI service type detection and capabilities assessment`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_parse_ai_service_response](ip, port, endpoint, content, service_name) - **NEW**: AI service response parsing and node creation`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_calculate_network_trust](ip) - **NEW**: Constitutional trust scoring for network services`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_perform_health_check](llm_node) - **NEW**: Continuous AI service health monitoring`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_register_local_ai_services]() - **NEW**: Register local AI services for discovery`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[_check_local_ollama]() - **NEW**: Detect and validate local Ollama installations`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[get_discovered_llm_nodes](trusted_only, healthy_only) - **NEW**: Retrieve discovered AI services with filtering`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[get_best_llm_node_for_model](model_name) - **NEW**: Intelligent AI service selection`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[get_available_models]() - **NEW**: Aggregate model availability across network`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[get_discovery_stats]() - **NEW**: Network AI discovery statistics and metrics`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[add_discovery_callback](callback) - **NEW**: Register callbacks for service discovery events`
- `[core/network/llm_discovery.py]::[LLMDiscovery]::[add_removal_callback](callback) - **NEW**: Register callbacks for service removal events`

**Utility Functions:**
- `[core/network/llm_discovery.py]::[create_llm_discovery_service](settings, node_id) - **NEW**: Factory for AI discovery service`

### core/network/p2p.py

**Classes:**
- `[core/network/p2p.py]::[MessageType] - P2P message types enumeration`
- `[core/network/p2p.py]::[P2PMessage] - Represents a P2P message with constitutional compliance`
- `[core/network/p2p.py]::[PeerConnection] - Represents a connection to a peer`
- `[core/network/p2p.py]::[P2PManager] - Constitutional P2P communication manager`

**P2PManager Methods:**
- `[core/network/p2p.py]::[P2PManager]::[__init__](settings, node_id, did) - Initialize P2P manager`
- `[core/network/p2p.py]::[P2PManager]::[start_p2p_service]() - Start P2P communication service`
- `[core/network/p2p.py]::[P2PManager]::[stop_p2p_service]() - Stop P2P communication service`
- `[core/network/p2p.py]::[P2PManager]::[connect_to_peer](node) - Establish connection to peer node`
- `[core/network/p2p.py]::[P2PManager]::[disconnect_from_peer](node_id) - Disconnect from specific peer`
- `[core/network/p2p.py]::[P2PManager]::[send_message](receiver_id, message_type, content) - Send message to specific peer`
- `[core/network/p2p.py]::[P2PManager]::[broadcast_message](message_type, content, trusted_only) - Broadcast message to all peers`
- `[core/network/p2p.py]::[P2PManager]::[add_message_handler](message_type, handler) - Add custom message handler`
- `[core/network/p2p.py]::[P2PManager]::[add_message_callback](callback) - Add message callback`
- `[core/network/p2p.py]::[P2PManager]::[get_connection_stats]() - Get P2P connection statistics`

**Utility Functions:**
- `[core/network/p2p.py]::[create_p2p_manager](settings, node_id, did) - Create constitutional P2P manager`

### core/network/encryption.py

**Classes:**
- `[core/network/encryption.py]::[EncryptionKeys] - Encryption key material for secure communication`
- `[core/network/encryption.py]::[SecureChannel] - Represents an encrypted communication channel`
- `[core/network/encryption.py]::[NoiseProtocol] - Noise Protocol implementation for P2P encryption`
- `[core/network/encryption.py]::[NetworkEncryption] - Constitutional network encryption manager`

**NoiseProtocol Methods:**
- `[core/network/encryption.py]::[NoiseProtocol]::[__init__]() - Initialize Noise Protocol handler`
- `[core/network/encryption.py]::[NoiseProtocol]::[generate_keypair]() - Generate X25519 key pair for Noise protocol`
- `[core/network/encryption.py]::[NoiseProtocol]::[perform_handshake](local_keys, remote_public_key_bytes) - Perform Noise protocol handshake`
- `[core/network/encryption.py]::[NoiseProtocol]::[encrypt_message](message, keys, nonce) - Encrypt message using Noise protocol`
- `[core/network/encryption.py]::[NoiseProtocol]::[decrypt_message](encrypted_message, keys) - Decrypt message using Noise protocol`

**NetworkEncryption Methods:**
- `[core/network/encryption.py]::[NetworkEncryption]::[__init__](settings, node_id) - Initialize network encryption`
- `[core/network/encryption.py]::[NetworkEncryption]::[_initialize_encryption]() - Initialize encryption components`
- `[core/network/encryption.py]::[NetworkEncryption]::[_setup_tls_context]() - Setup TLS 1.3 context for transport security`
- `[core/network/encryption.py]::[NetworkEncryption]::[get_public_key_bytes]() - Get local public key for sharing with peers`
- `[core/network/encryption.py]::[NetworkEncryption]::[create_secure_channel](peer_id, remote_public_key_bytes) - Create secure channel with peer`
- `[core/network/encryption.py]::[NetworkEncryption]::[encrypt_for_channel](channel_id, message) - Encrypt message for specific channel`
- `[core/network/encryption.py]::[NetworkEncryption]::[decrypt_from_channel](channel_id, encrypted_message) - Decrypt message from specific channel`
- `[core/network/encryption.py]::[NetworkEncryption]::[close_channel](channel_id) - Close secure communication channel`
- `[core/network/encryption.py]::[NetworkEncryption]::[wrap_connection_with_tls](reader, writer) - Wrap connection with TLS encryption`
- `[core/network/encryption.py]::[NetworkEncryption]::[cleanup_expired_channels]() - Clean up expired channels for security`
- `[core/network/encryption.py]::[NetworkEncryption]::[_generate_channel_id](peer_id) - Generate unique channel ID`
- `[core/network/encryption.py]::[NetworkEncryption]::[get_encryption_stats]() - Get encryption statistics`

**Utility Functions:**
- `[core/network/encryption.py]::[create_network_encryption](settings, node_id) - Create constitutional network encryption`

---

## Storage System

### core/storage/database.py

**Classes:**
- `[core/storage/database.py]::[DataRecord] - Represents a data record with constitutional compliance`
- `[core/storage/database.py]::[ConstitutionalMetadata] - Metadata for constitutional compliance tracking`
- `[core/storage/database.py]::[ConstitutionalDatabase] - Constitutional-compliant database interface`
- `[core/storage/database.py]::[DatabaseManager] - Manages database operations with constitutional compliance`

**ConstitutionalDatabase Methods:**
- `[core/storage/database.py]::[ConstitutionalDatabase]::[__init__](db_path, settings) - Initialize constitutional database`
- `[core/storage/database.py]::[ConstitutionalDatabase]::[create_record](data, metadata, user_consent) - Create data record with compliance`
- `[core/storage/database.py]::[ConstitutionalDatabase]::[read_record](record_id, user_consent) - Read record with privacy protection`
- `[core/storage/database.py]::[ConstitutionalDatabase]::[update_record](record_id, data, user_consent) - Update record with audit trail`
- `[core/storage/database.py]::[ConstitutionalDatabase]::[delete_record](record_id, user_requested) - Delete record with compliance`
- `[core/storage/database.py]::[ConstitutionalDatabase]::[search_records](query, user_consent) - Search records with privacy protection`

**DatabaseManager Methods:**
- `[core/storage/database.py]::[DatabaseManager]::[__init__](settings) - Initialize database manager`
- `[core/storage/database.py]::[DatabaseManager]::[get_connection](db_name) - Get database connection`
- `[core/storage/database.py]::[DatabaseManager]::[create_database](db_name) - Create new database`
- `[core/storage/database.py]::[DatabaseManager]::[backup_database](db_name) - Backup database with encryption`
- `[core/storage/database.py]::[DatabaseManager]::[get_audit_trail](record_id) - Get audit trail for record`

**Utility Functions:**
- `[core/storage/database.py]::[create_database_manager](settings) - Create constitutional database manager`

### core/storage/vector_store.py

**Classes:**
- `[core/storage/vector_store.py]::[VectorDocument] - Represents a document with vector embedding`
- `[core/storage/vector_store.py]::[VectorSearchResult] - Search result with similarity score`
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore] - Constitutional-compliant vector store`
- `[core/storage/vector_store.py]::[VectorStore] - Vector database manager with constitutional compliance`

**ConstitutionalVectorStore Methods:**
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore]::[__init__](collection_name, dimension, settings) - Initialize vector store`
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore]::[add_document](doc_id, text, embedding, metadata) - Add document with privacy protection`
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore]::[search](query_embedding, limit, filter_dict) - Search vectors with constitutional compliance`
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore]::[delete_document](doc_id, user_requested) - Delete document with audit trail`
- `[core/storage/vector_store.py]::[ConstitutionalVectorStore]::[get_document](doc_id) - Get document with privacy checks`

**VectorStore Methods:**
- `[core/storage/vector_store.py]::[VectorStore]::[__init__](settings) - Initialize vector store manager`
- `[core/storage/vector_store.py]::[VectorStore]::[create_store](collection_name, dimension) - Create new vector store collection`
- `[core/storage/vector_store.py]::[VectorStore]::[get_store](collection_name) - Get existing vector store`
- `[core/storage/vector_store.py]::[VectorStore]::[delete_store](collection_name) - Delete vector store collection`
- `[core/storage/vector_store.py]::[VectorStore]::[list_stores]() - List all vector store collections`

**Utility Functions:**
- `[core/storage/vector_store.py]::[create_vector_store](settings) - Create constitutional vector store manager`

---

## AI System

This section details the components of the HAI-Net AI system, which is architected around the event-driven, multi-agent principles of the TrippleEffect framework.

### Core Agent Components (`core/ai/agents.py`)

This file defines the fundamental building blocks of the agentic system.

**Classes:**
- `[core/ai/agents.py]::[AgentState] - Enum for agent states, inspired by the TrippleEffect state machine (e.g., IDLE, PLANNING, WORK, MANAGE).`
- `[core/ai/agents.py]::[AgentRole] - Enum for agent roles, aligned with the TrippleEffect hierarchy (ADMIN, PM, WORKER, GUARDIAN).`
- `[core/ai/agents.py]::[AgentCapability] - Enum for specific agent skills (e.g., CODE_GENERATION, RESEARCH).`
- `[core/ai/agents.py]::[AgentMetrics] - Dataclass for agent performance and health metrics.`
- `[core/ai/agents.py]::[AgentStateTransitions] - Class managing valid state transitions for agents based on their roles and workflows.`
- `[core/ai/agents.py]::[Agent] - The core constitutional AI agent class, featuring a state machine and an event-yielding processing method.`
- `[core/ai/agents.py]::[AgentManager] - The central orchestrator for the agent framework, responsible for agent lifecycle, scheduling, and serving as a hub for handlers.`

**Agent Methods:**
- `[core/ai/agents.py]::[Agent]::[__init__](...) - Initializes a constitutional agent with a role, state, and capabilities.`
- `[core/ai/agents.py]::[Agent]::[start]() / [stop]() - Manages the agent's lifecycle.`
- `[core/ai/agents.py]::[Agent]::[process_message](messages) - **CRITICAL**: The core async generator that yields events (thoughts, tool requests, responses) for the `AgentCycleHandler` to process.`
- `[core/ai/agents.py]::[Agent]::[get_status]() - Returns the agent's current status and metrics.`

**AgentManager Methods:**
- `[core/ai/agents.py]::[AgentManager]::[__init__](settings, llm_manager) - Initializes the manager.`
- `[core/ai/agents.py]::[AgentManager]::[set_handlers](cycle_handler, workflow_manager) - Injects the core handlers for agent execution.`
- `[core/ai/agents.py]::[AgentManager]::[create_agent](role, ...) - Creates, starts, and registers a new agent.`
- `[core/ai/agents.py]::[AgentManager]::[handle_user_message](user_input, ...) - The primary entry point for user interaction, which routes input to the ADMIN agent.`
- `[core/ai/agents.py]::[AgentManager]::[schedule_cycle](agent_id) - **CRITICAL**: Schedules an agent to be run by the `AgentCycleHandler`.`

### Agent Execution Handlers

These components manage the agent execution loop, tool interactions, and high-level workflows.

**`core/ai/cycle_handler.py`**
- `[core/ai/cycle_handler.py]::[AgentCycleHandler] - The engine of the agent framework. It runs an agent's execution cycle.`
- `[core/ai/cycle_handler.py]::[AgentCycleHandler]::[__init__](...) - Initializes with interaction, workflow, and guardian handlers.`
- `[core/ai/cycle_handler.py]::[AgentCycleHandler]::[run_cycle](agent) - **CRITICAL**: Manages the agent's state, consumes events from `agent.process_message`, and orchestrates actions like tool calls and state changes.`

**`core/ai/interaction_handler.py`**
- `[core/ai/interaction_handler.py]::[InteractionHandler] - Mediates between the `AgentCycleHandler` and the `ToolExecutor`.`
- `[core/ai/interaction_handler.py]::[InteractionHandler]::[__init__](settings, tool_executor) - Initializes with the tool executor.`
- `[core/ai/interaction_handler.py]::[InteractionHandler]::[execute_tool_call](agent, tool_call) - Executes a tool call, injecting the calling agent's context into the tool's arguments.`

**`core/ai/workflow_manager.py`**
- `[core/ai/workflow_manager.py]::[WorkflowManager] - Manages agent state transitions and orchestrates high-level, multi-agent workflows.`
- `[core/ai/workflow_manager.py]::[WorkflowManager]::[__init__](settings) - Initializes the manager.`
- `[core/ai/workflow_manager.py]::[WorkflowManager]::[change_agent_state](agent, new_state) - Safely transitions an agent to a new state.`
- `[core/ai/workflow_manager.py]::[WorkflowManager]::[process_agent_output_for_workflow](agent, output) - Analyzes agent output for triggers that start complex workflows (e.g., project creation).`

### Agent Tools

These components provide agents with the capabilities to interact with their environment and each other.

**`core/ai/tools/executor.py`**
- `[core/ai/tools/executor.py]::[ToolExecutor] - Discovers, registers, and executes tools available to agents.`
- `[core/ai/tools/executor.py]::[ToolExecutor]::[__init__](settings, agent_manager) - Initializes and auto-discovers tools.`
- `[core/ai/tools/executor.py]::[ToolExecutor]::[execute_tool](name, args) - Executes a tool by name with the provided arguments.`

**`core/ai/tools/communication.py`**
- `[core/ai/tools/communication.py]::[SendMessageTool] - A tool that allows agents to communicate with each other.`
- `[core/ai/tools/communication.py]::[SendMessageTool]::[execute](sender_agent, target_agent_id, message) - Sends a message to a target agent's message history and schedules them for execution.`

### Supporting AI Components

These components provide foundational AI capabilities like LLM access, memory, and compliance.

**`core/ai/llm.py`**
- `[core/ai/llm.py]::[LLMManager] - Manages interaction with LLM providers like Ollama.`
- `[core/ai/llm.py]::[LLMManager]::[stream_response](...) - Streams a response from an LLM, which is consumed by the `Agent.process_message` method.`

**`core/ai/memory.py`**
- `[core/ai/memory.py]::[MemoryManager] - Manages the different types of memory for each agent.`

**`core/ai/guardian.py`**
- `[core/ai/guardian.py]::[ConstitutionalGuardian] - The independent monitor that ensures all agent actions comply with the HAI-Net constitution.`

---

## Web Interface

### core/web/server.py

**Classes:**
- `[core/web/server.py]::[WebServer] - Constitutional web server with FastAPI`

**WebServer Methods:**
- `[core/web/server.py]::[WebServer]::[__init__](settings) - Initialize constitutional web server`
- `[core/web/server.py]::[WebServer]::[start](host, port) - Start the web server`
- `[core/web/server.py]::[WebServer]::[stop]() - Stop the web server gracefully`
- `[core/web/server.py]::[WebServer]::[broadcast_websocket_message](message) - Broadcast message to all WebSocket clients`

**API Endpoints:**
- `[core/web/server.py]::[health_check]() - System health check endpoint`
- `[core/web/server.py]::[constitutional_status]() - Get constitutional compliance status`
- `[core/web/server.py]::[get_agents]() - Get all agents with constitutional protection`
- `[core/web/server.py]::[create_agent](request) - Create new agent with constitutional validation`
- `[core/web/server.py]::[chat_with_ai](request) - Chat with constitutional AI`
- `[core/web/server.py]::[network_status]() - Get P2P network status`
- `[core/web/server.py]::[get_agent_memory](agent_id) - Get agent memory summary with privacy protection`
- `[core/web/server.py]::[search_agent_memory](agent_id, request) - Search agent memory with constitutional compliance`
- `[core/web/server.py]::[get_settings]() - Get non-sensitive settings`
- `[core/web/server.py]::[websocket_endpoint](websocket, client_id) - WebSocket connection for real-time updates`

**Utility Functions:**
- `[core/web/server.py]::[create_web_server](settings) - Create constitutional web server`

### web/templates/index.html

**Web Interface:**
- `[web/templates/index.html] - Constitutional web dashboard with interactive API testing`
- Features: Constitutional theme, system status, agent management, network visualization, compliance monitoring
- Interactive JavaScript functions for API testing and system monitoring

---
<!-- # END OF FILE helperfiles/FUNCTIONS_INDEX.md -->
