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

### core/ai/llm.py

**Classes:**
- `[core/ai/llm.py]::[LLMProvider] - Supported LLM providers enumeration`
- `[core/ai/llm.py]::[LLMResponse] - Response from LLM inference with constitutional compliance`
- `[core/ai/llm.py]::[LLMMessage] - Message for LLM conversation`
- `[core/ai/llm.py]::[LLMModelInfo] - Information about an available LLM model`
- `[core/ai/llm.py]::[ConstitutionalLLMFilter] - Filters LLM responses for constitutional compliance`
- `[core/ai/llm.py]::[OllamaProvider] - Ollama LLM provider with constitutional compliance`
- `[core/ai/llm.py]::[LLMManager] - Constitutional LLM manager for AI services`

**ConstitutionalLLMFilter Methods:**
- `[core/ai/llm.py]::[ConstitutionalLLMFilter]::[__init__](settings) - Initialize constitutional filter`
- `[core/ai/llm.py]::[ConstitutionalLLMFilter]::[filter_request](messages, user_did) - Filter incoming requests`
- `[core/ai/llm.py]::[ConstitutionalLLMFilter]::[filter_response](response, user_did) - Filter outgoing responses`
- `[core/ai/llm.py]::[ConstitutionalLLMFilter]::[check_privacy_compliance](content) - Check privacy compliance`
- `[core/ai/llm.py]::[ConstitutionalLLMFilter]::[check_human_rights_compliance](content) - Check human rights compliance`

**OllamaProvider Methods:**
- `[core/ai/llm.py]::[OllamaProvider]::[__init__](settings) - Initialize Ollama provider`
- `[core/ai/llm.py]::[OllamaProvider]::[initialize]() - Initialize Ollama provider`
- `[core/ai/llm.py]::[OllamaProvider]::[generate_response](messages, model, user_did) - Generate response with constitutional compliance`
- `[core/ai/llm.py]::[OllamaProvider]::[stream_response](messages, model, user_did) - Stream response with compliance`
- `[core/ai/llm.py]::[OllamaProvider]::[get_available_models]() - Get list of available models`
- `[core/ai/llm.py]::[OllamaProvider]::[close]() - Close the provider`

**LLMManager Methods:**
- `[core/ai/llm.py]::[LLMManager]::[__init__](settings) - Initialize LLM manager`
- `[core/ai/llm.py]::[LLMManager]::[initialize]() - Initialize LLM manager and providers`
- `[core/ai/llm.py]::[LLMManager]::[generate_response](messages, model, user_did) - Generate response with constitutional compliance`
- `[core/ai/llm.py]::[LLMManager]::[stream_response](messages, model, user_did) - Stream response with compliance`
- `[core/ai/llm.py]::[LLMManager]::[get_available_models]() - Get all available models`
- `[core/ai/llm.py]::[LLMManager]::[close]() - Close all providers`

**Utility Functions:**
- `[core/ai/llm.py]::[create_llm_manager](settings) - Create constitutional LLM manager`

### core/ai/memory.py

**Classes:**
- `[core/ai/memory.py]::[MemoryType] - Types of memories enumeration`
- `[core/ai/memory.py]::[MemoryImportance] - Importance levels for memory retention`
- `[core/ai/memory.py]::[Memory] - Represents a single memory with constitutional compliance`
- `[core/ai/memory.py]::[MemoryManager] - Constitutional memory manager for AI agents`

**MemoryManager Methods:**
- `[core/ai/memory.py]::[MemoryManager]::[__init__](settings, vector_store) - Initialize memory manager`
- `[core/ai/memory.py]::[MemoryManager]::[store_memory](agent_id, content, memory_type, importance, metadata) - Store memory with constitutional compliance`
- `[core/ai/memory.py]::[MemoryManager]::[retrieve_memory](agent_id, memory_id) - Retrieve specific memory by ID`
- `[core/ai/memory.py]::[MemoryManager]::[search_memories](agent_id, query, memory_type, limit) - Search memories with constitutional compliance`
- `[core/ai/memory.py]::[MemoryManager]::[delete_memory](agent_id, memory_id, user_requested) - Delete memory with constitutional protection`
- `[core/ai/memory.py]::[MemoryManager]::[get_agent_memory_summary](agent_id) - Get summary of agent's memories`
- `[core/ai/memory.py]::[MemoryManager]::[cleanup_expired_memories]() - Clean up expired memories across all agents`

**Utility Functions:**
- `[core/ai/memory.py]::[create_memory_manager](settings, vector_store) - Create constitutional memory manager`

### core/ai/guardian.py

**Classes:**
- `[core/ai/guardian.py]::[ViolationType] - Types of constitutional violations`
- `[core/ai/guardian.py]::[ViolationSeverity] - Severity levels for violations`
- `[core/ai/guardian.py]::[ConstitutionalViolation] - Represents a constitutional violation`
- `[core/ai/guardian.py]::[ComplianceMetrics] - Constitutional compliance metrics`
- `[core/ai/guardian.py]::[ConstitutionalGuardian] - Independent constitutional compliance monitor`

**ConstitutionalGuardian Methods:**
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[__init__](settings, guardian_agent) - Initialize constitutional guardian`
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[start_monitoring]() - Start constitutional monitoring`
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[stop_monitoring]() - Stop constitutional monitoring`
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[report_violation](violation_type, severity, principle_violated, description) - Report constitutional violation`
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[get_compliance_metrics]() - Get current compliance metrics`
- `[core/ai/guardian.py]::[ConstitutionalGuardian]::[add_remediation_callback](callback) - Add remediation callback`

**Utility Functions:**
- `[core/ai/guardian.py]::[create_constitutional_guardian](settings, guardian_agent) - Create constitutional guardian`

### core/ai/agents.py

**Classes:**
- `[core/ai/agents.py]::[AgentState] - Agent state machine states enumeration`
- `[core/ai/agents.py]::[AgentRole] - Agent roles in HAI-Net hierarchy`
- `[core/ai/agents.py]::[AgentCapability] - Agent capabilities enumeration`
- `[core/ai/agents.py]::[AgentMemory] - Agent memory structure`
- `[core/ai/agents.py]::[AgentTask] - Represents a task for an agent`
- `[core/ai/agents.py]::[AgentMetrics] - Agent performance and health metrics`
- `[core/ai/agents.py]::[AgentStateTransitions] - Manages valid state transitions for agents`
- `[core/ai/agents.py]::[Agent] - Constitutional AI Agent with state machine`
- `[core/ai/agents.py]::[AgentManager] - Constitutional Agent Manager for HAI-Net`

**AgentStateTransitions Methods:**
- `[core/ai/agents.py]::[AgentStateTransitions]::[is_valid_transition](from_state, to_state) - Check if state transition is valid`
- `[core/ai/agents.py]::[AgentStateTransitions]::[get_valid_transitions](from_state) - Get list of valid transitions`

**Agent Methods:**
- `[core/ai/agents.py]::[Agent]::[__init__](agent_id, role, settings, llm_manager, user_did) - Initialize constitutional agent`
- `[core/ai/agents.py]::[Agent]::[start]() - Start the agent`
- `[core/ai/agents.py]::[Agent]::[stop]() - Stop the agent`
- `[core/ai/agents.py]::[Agent]::[assign_task](task) - Assign a task to the agent`
- `[core/ai/agents.py]::[Agent]::[get_status]() - Get current agent status`
- `[core/ai/agents.py]::[Agent]::[add_state_change_callback](callback) - Add callback for state changes`

**AgentManager Methods:**
- `[core/ai/agents.py]::[AgentManager]::[__init__](settings, llm_manager) - Initialize agent manager`
- `[core/ai/agents.py]::[AgentManager]::[create_agent](role, user_did, capabilities) - Create a new agent with constitutional compliance`
- `[core/ai/agents.py]::[AgentManager]::[remove_agent](agent_id) - Remove an agent`
- `[core/ai/agents.py]::[AgentManager]::[assign_task_to_agent](agent_id, task) - Assign task to specific agent`
- `[core/ai/agents.py]::[AgentManager]::[assign_task_by_capability](task, required_capability) - Assign task by capability`
- `[core/ai/agents.py]::[AgentManager]::[get_agent](agent_id) - Get agent by ID`
- `[core/ai/agents.py]::[AgentManager]::[get_agents_by_role](role) - Get agents by role`
- `[core/ai/agents.py]::[AgentManager]::[get_all_agents]() - Get all agents`
- `[core/ai/agents.py]::[AgentManager]::[get_manager_stats]() - Get agent manager statistics`

**Utility Functions:**
- `[core/ai/agents.py]::[create_agent_manager](settings, llm_manager) - Create constitutional agent manager`

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
