# START OF FILE core/ai/llm.py
"""
HAI-Net LLM Management
Constitutional compliance: Privacy First + Human Rights + Decentralization
Local LLM inference with constitutional protection
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

try:
    import aiohttp  # type: ignore
except ImportError:
    aiohttp = None  # type: ignore

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    OPENAI_COMPATIBLE = "openai_compatible"
    LOCAL_TRANSFORMERS = "local_transformers"


@dataclass
class LLMResponse:
    """Response from LLM inference"""
    content: str
    model: str
    provider: LLMProvider
    tokens_used: int
    response_time_ms: float
    constitutional_compliant: bool
    privacy_protected: bool
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LLMMessage:
    """Message for LLM conversation"""
    role: str  # system, user, assistant
    content: str
    timestamp: float
    constitutional_checked: bool = False


@dataclass
class LLMModelInfo:
    """Information about an available LLM model"""
    name: str
    provider: LLMProvider
    size_gb: float
    capabilities: List[str]
    constitutional_approved: bool
    privacy_level: str  # local, remote, hybrid
    context_length: int
    description: str


class ConstitutionalLLMFilter:
    """
    Constitutional compliance filter for LLM interactions
    Ensures all AI interactions comply with constitutional principles
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.llm.filter", settings)
        self.constitutional_version = "1.0"
        
        # Constitutional compliance patterns
        self.privacy_violations = [
            "personal information", "private data", "confidential",
            "social security", "credit card", "password", "api key"
        ]
        
        self.harmful_content = [
            "violence", "hate speech", "discrimination", "illegal activities",
            "misinformation", "harmful instructions", "dangerous content"
        ]
        
        self.human_rights_violations = [
            "surveillance", "tracking", "manipulation", "coercion",
            "privacy invasion", "rights violation", "discrimination"
        ]
    
    def check_prompt_compliance(self, prompt: str, user_did: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if prompt complies with constitutional principles
        
        Args:
            prompt: User prompt to check
            user_did: Optional user DID for audit trail
            
        Returns:
            Dict with compliance status and details
        """
        try:
            violations_list: List[Dict[str, Any]] = []
            compliance_result: Dict[str, Any] = {
                "compliant": True,
                "violations": violations_list,
                "warnings": [],
                "modified_prompt": prompt,
                "privacy_protected": True,
                "human_rights_respected": True
            }
            
            prompt_lower = prompt.lower()
            
            # Check for privacy violations
            privacy_issues: List[str] = []
            for pattern in self.privacy_violations:
                if pattern in prompt_lower:
                    privacy_issues.append(pattern)
            
            if privacy_issues:
                violations_list.append({
                    "type": "privacy_violation",
                    "principle": "Privacy First",
                    "issues": privacy_issues,
                    "severity": "high"
                })
                compliance_result["compliant"] = False
                compliance_result["privacy_protected"] = False
            
            # Check for harmful content
            harmful_issues: List[str] = []
            for pattern in self.harmful_content:
                if pattern in prompt_lower:
                    harmful_issues.append(pattern)
            
            if harmful_issues:
                violations_list.append({
                    "type": "harmful_content",
                    "principle": "Human Rights",
                    "issues": harmful_issues,
                    "severity": "high"
                })
                compliance_result["compliant"] = False
                compliance_result["human_rights_respected"] = False
            
            # Check for human rights violations
            rights_issues: List[str] = []
            for pattern in self.human_rights_violations:
                if pattern in prompt_lower:
                    rights_issues.append(pattern)
            
            if rights_issues:
                violations_list.append({
                    "type": "human_rights_violation",
                    "principle": "Human Rights",
                    "issues": rights_issues,
                    "severity": "high"
                })
                compliance_result["compliant"] = False
                compliance_result["human_rights_respected"] = False
            
            # Log compliance check
            self.logger.log_privacy_event(
                "prompt_compliance_check",
                f"result_{compliance_result['compliant']}",
                user_consent=True
            )
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return {
                "compliant": False,
                "violations": [{"type": "check_error", "message": str(e)}],
                "warnings": [],
                "modified_prompt": prompt,
                "privacy_protected": False,
                "human_rights_respected": False
            }
    
    def check_response_compliance(self, response: str, model: str) -> Dict[str, Any]:
        """
        Check if LLM response complies with constitutional principles
        
        Args:
            response: LLM response to check
            model: Model that generated the response
            
        Returns:
            Dict with compliance status and details
        """
        try:
            violations_list: List[Dict[str, Any]] = []
            compliance_result: Dict[str, Any] = {
                "compliant": True,
                "violations": violations_list,
                "warnings": [],
                "filtered_response": response,
                "privacy_protected": True,
                "human_rights_respected": True
            }
            
            response_lower = response.lower()
            
            # Check for leaked private information
            privacy_leaks: List[str] = []
            for pattern in self.privacy_violations:
                if pattern in response_lower:
                    privacy_leaks.append(pattern)
            
            if privacy_leaks:
                violations_list.append({
                    "type": "privacy_leak",
                    "principle": "Privacy First",
                    "issues": privacy_leaks,
                    "severity": "critical"
                })
                compliance_result["compliant"] = False
                compliance_result["privacy_protected"] = False
                # Filter out the response
                compliance_result["filtered_response"] = "[RESPONSE FILTERED: Privacy violation detected]"
            
            # Check for harmful content generation
            harmful_content: List[str] = []
            for pattern in self.harmful_content:
                if pattern in response_lower:
                    harmful_content.append(pattern)
            
            if harmful_content:
                violations_list.append({
                    "type": "harmful_content_generation",
                    "principle": "Human Rights",
                    "issues": harmful_content,
                    "severity": "high"
                })
                compliance_result["compliant"] = False
                compliance_result["human_rights_respected"] = False
                # Filter response partially
                compliance_result["filtered_response"] = "[RESPONSE FILTERED: Potentially harmful content detected]"
            
            # Log response compliance check
            self.logger.log_privacy_event(
                "response_compliance_check",
                f"model_{model}_result_{compliance_result['compliant']}",
                user_consent=True
            )
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Response compliance check failed: {e}")
            return {
                "compliant": False,
                "violations": [{"type": "check_error", "message": str(e)}],
                "warnings": [],
                "filtered_response": response,
                "privacy_protected": False,
                "human_rights_respected": False
            }


class OllamaProvider:
    """
    Ollama LLM provider with constitutional compliance
    Local-first AI inference respecting privacy and human rights
    """
    
    def __init__(self, settings: HAINetSettings, base_url: str = "http://localhost:11434"):
        self.settings = settings
        self.base_url = base_url
        self.logger = get_logger("ai.llm.ollama", settings)
        self.session: Any = None
        self.available_models: List[LLMModelInfo] = []
        
        # Constitutional compliance
        self.filter = ConstitutionalLLMFilter(settings)
        self.constitutional_version = "1.0"
    
    async def initialize(self) -> bool:
        """Initialize Ollama provider"""
        try:
            if aiohttp is None:
                self.logger.error("aiohttp is not installed, cannot initialize Ollama provider")
                return False
            self.session = aiohttp.ClientSession()  # type: ignore
            
            # Check if Ollama is running
            if not await self._check_ollama_availability():
                self.logger.warning("Ollama service not available")
                return False
            
            # Load available models
            await self._load_available_models()
            
            self.logger.log_decentralization_event(
                "ollama_provider_initialized",
                local_processing=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ollama initialization failed: {e}")
            return False
    
    async def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is running"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def _load_available_models(self):
        """Load list of available Ollama models"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    
                    self.available_models = []
                    for model_data in models:
                        model_info = LLMModelInfo(
                            name=model_data["name"],
                            provider=LLMProvider.OLLAMA,
                            size_gb=model_data.get("size", 0) / (1024 * 1024 * 1024),
                            capabilities=["text_generation", "conversation"],
                            constitutional_approved=True,  # Local models are constitutionally approved
                            privacy_level="local",
                            context_length=model_data.get("details", {}).get("parameter_size", 4096),
                            description=f"Ollama model: {model_data['name']}"
                        )
                        self.available_models.append(model_info)
                    
                    self.logger.info(f"Loaded {len(self.available_models)} Ollama models")
                    
        except Exception as e:
            self.logger.error(f"Failed to load Ollama models: {e}")
    
    async def generate_response(self, messages: List[LLMMessage], model: str,
                              user_did: Optional[str] = None,
                              max_tokens: int = 1000,
                              temperature: float = 0.7) -> LLMResponse:
        """
        Generate response using Ollama with constitutional compliance
        
        Args:
            messages: Conversation messages
            model: Model name to use
            user_did: Optional user DID for audit trail
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            LLM response with constitutional compliance
        """
        try:
            start_time = time.time()
            
            # Check constitutional compliance of the prompt
            if messages:
                last_message = messages[-1]
                compliance_check = self.filter.check_prompt_compliance(
                    last_message.content, user_did
                )
                
                if not compliance_check["compliant"]:
                    self.logger.log_violation("llm_prompt_violation", {
                        "user_did": user_did,
                        "violations": compliance_check["violations"]
                    })
                    
                    return LLMResponse(
                        content="I cannot process this request as it violates constitutional principles. Please rephrase your request in a way that respects privacy and human rights.",
                        model=model,
                        provider=LLMProvider.OLLAMA,
                        tokens_used=0,
                        response_time_ms=0,
                        constitutional_compliant=False,
                        privacy_protected=True,
                        timestamp=time.time(),
                        metadata={"violations": compliance_check["violations"]}
                    )
            
            # Prepare request for Ollama
            ollama_messages: List[Dict[str, str]] = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            request_data: Dict[str, Any] = {
                "model": model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            # Make request to Ollama
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=60
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"Ollama request failed: {response.status}")
                
                data = await response.json()
                response_content = data["message"]["content"]
                
                # Check constitutional compliance of response
                response_compliance = self.filter.check_response_compliance(
                    response_content, model
                )
                
                # Calculate response time
                response_time_ms = (time.time() - start_time) * 1000
                
                # Log the interaction
                self.logger.log_privacy_event(
                    "llm_generation_local",
                    f"model_{model}",
                    user_consent=True
                )
                
                return LLMResponse(
                    content=response_compliance["filtered_response"],
                    model=model,
                    provider=LLMProvider.OLLAMA,
                    tokens_used=data.get("eval_count", 0),
                    response_time_ms=response_time_ms,
                    constitutional_compliant=response_compliance["compliant"],
                    privacy_protected=response_compliance["privacy_protected"],
                    timestamp=time.time(),
                    metadata={
                        "eval_duration": data.get("eval_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "compliance_check": response_compliance
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            
            return LLMResponse(
                content="I apologize, but I'm currently unable to process your request due to a technical issue. Please try again later.",
                model=model,
                provider=LLMProvider.OLLAMA,
                tokens_used=0,
                response_time_ms=0,
                constitutional_compliant=True,
                privacy_protected=True,
                timestamp=time.time(),
                metadata={"error": str(e)}
            )
    
    async def stream_response(self, messages: List[LLMMessage], model: str,
                            user_did: Optional[str] = None,
                            max_tokens: int = 1000,
                            temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """
        Stream response from Ollama with constitutional compliance
        
        Args:
            messages: Conversation messages
            model: Model name to use
            user_did: Optional user DID for audit trail
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Response chunks
        """
        try:
            # Check constitutional compliance first
            if messages:
                last_message = messages[-1]
                compliance_check = self.filter.check_prompt_compliance(
                    last_message.content, user_did
                )
                
                if not compliance_check["compliant"]:
                    yield "I cannot process this request as it violates constitutional principles."
                    return
            
            # Prepare request for Ollama streaming
            ollama_messages: List[Dict[str, str]] = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            request_data: Dict[str, Any] = {
                "model": model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            # Stream response from Ollama
            full_response = ""
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=120
            ) as response:
                
                if response.status != 200:
                    yield "Error: Unable to connect to AI service."
                    return
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode().strip())
                            if "message" in data and "content" in data["message"]:
                                chunk = data["message"]["content"]
                                full_response += chunk
                                
                                # Basic constitutional filter for chunks
                                if not any(violation in chunk.lower() for violation in self.filter.privacy_violations):
                                    yield chunk
                                
                        except json.JSONDecodeError:
                            continue
            
            # Final compliance check on complete response
            if full_response:
                response_compliance = self.filter.check_response_compliance(
                    full_response, model
                )
                
                if not response_compliance["compliant"]:
                    self.logger.log_violation("llm_response_violation", {
                        "model": model,
                        "user_did": user_did,
                        "violations": response_compliance["violations"]
                    })
                
                # Log the streaming interaction
                self.logger.log_privacy_event(
                    "llm_streaming_local",
                    f"model_{model}",
                    user_consent=True
                )
                
        except Exception as e:
            self.logger.error(f"Ollama streaming failed: {e}")
            yield "I apologize, but I'm currently unable to process your request."
    
    def get_available_models(self) -> List[LLMModelInfo]:
        """Get list of available models"""
        return self.available_models.copy()
    
    async def close(self):
        """Close the provider"""
        if self.session:
            await self.session.close()


class LLMManager:
    """
    Constitutional LLM manager for HAI-Net
    Manages multiple LLM providers with constitutional compliance
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.llm.manager", settings)
        
        # Providers
        self.providers: Dict[LLMProvider, Any] = {}
        self.available_models: List[LLMModelInfo] = []
        
        # Constitutional compliance
        self.filter = ConstitutionalLLMFilter(settings)
        self.constitutional_version = "1.0"
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "constitutional_violations": 0,
            "privacy_violations": 0
        }
        
        # Thread safety
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize LLM manager and providers"""
        try:
            async with self._lock:
                # Initialize Ollama provider, checking for settings safely
                if getattr(self.settings, 'ollama_enabled', False):
                    ollama_base_url = getattr(self.settings, 'ollama_base_url', "http://localhost:11434")
                    ollama_provider = OllamaProvider(
                        self.settings,
                        ollama_base_url
                    )
                    
                    if await ollama_provider.initialize():
                        self.providers[LLMProvider.OLLAMA] = ollama_provider
                        self.available_models.extend(ollama_provider.get_available_models())
                        self.logger.info("Ollama provider initialized successfully")
                    else:
                        self.logger.warning("Failed to initialize Ollama provider")
                
                # TODO: Add other providers (llama.cpp, OpenAI compatible, etc.)
                
                self.logger.log_decentralization_event(
                    "llm_manager_initialized",
                    local_processing=True
                )
                
                return len(self.providers) > 0
                
        except Exception as e:
            self.logger.error(f"LLM manager initialization failed: {e}")
            return False
    
    async def generate_response(self, messages: List[LLMMessage], model: str,
                              user_did: Optional[str] = None,
                              provider: Optional[LLMProvider] = None,
                              **kwargs: Any) -> LLMResponse:
        """
        Generate response using specified model and provider
        
        Args:
            messages: Conversation messages
            model: Model name to use
            user_did: Optional user DID for audit trail
            provider: Optional specific provider to use
            **kwargs: Additional parameters for generation
            
        Returns:
            LLM response with constitutional compliance
        """
        try:
            async with self._lock:
                self.usage_stats["total_requests"] += 1
                
                # Determine provider if not specified
                if provider is None:
                    provider = self._get_provider_for_model(model)
                
                if provider not in self.providers:
                    raise Exception(f"Provider {provider} not available")
                
                # Generate response
                response = await self.providers[provider].generate_response(
                    messages=messages,
                    model=model,
                    user_did=user_did,
                    **kwargs
                )
                
                # Update usage stats
                self.usage_stats["total_tokens"] += response.tokens_used
                if not response.constitutional_compliant:
                    self.usage_stats["constitutional_violations"] += 1
                if not response.privacy_protected:
                    self.usage_stats["privacy_violations"] += 1
                
                return response
                
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            
            return LLMResponse(
                content="I apologize, but I'm currently unable to process your request. Please try again later.",
                model=model,
                provider=provider or LLMProvider.OLLAMA,
                tokens_used=0,
                response_time_ms=0,
                constitutional_compliant=True,
                privacy_protected=True,
                timestamp=time.time(),
                metadata={"error": str(e)}
            )
    
    async def stream_response(self, messages: List[LLMMessage], model: str,
                            user_did: Optional[str] = None,
                            provider: Optional[LLMProvider] = None,
                            **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Stream response using specified model and provider
        
        Args:
            messages: Conversation messages
            model: Model name to use
            user_did: Optional user DID for audit trail
            provider: Optional specific provider to use
            **kwargs: Additional parameters for generation
            
        Yields:
            Response chunks
        """
        try:
            # Determine provider if not specified
            if provider is None:
                provider = self._get_provider_for_model(model)
            
            if provider not in self.providers:
                yield "Error: AI provider not available."
                return
            
            # Stream response
            async for chunk in self.providers[provider].stream_response(
                messages=messages,
                model=model,
                user_did=user_did,
                **kwargs
            ):
                yield chunk
                
        except Exception as e:
            self.logger.error(f"LLM streaming failed: {e}")
            yield "I apologize, but I'm currently unable to process your request."
    
    def _get_provider_for_model(self, model: str) -> LLMProvider:
        """Determine which provider to use for a given model"""
        # Simple heuristic - improve this with model registry
        for model_info in self.available_models:
            if model_info.name == model:
                return model_info.provider
        
        # Default to Ollama if available
        if LLMProvider.OLLAMA in self.providers:
            return LLMProvider.OLLAMA
        
        # Return first available provider
        if self.providers:
            return list(self.providers.keys())[0]
        
        return LLMProvider.OLLAMA
    
    def get_available_models(self) -> List[LLMModelInfo]:
        """Get list of all available models"""
        return self.available_models.copy()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats.copy()
    
    async def close(self):
        """Close all providers"""
        for provider in self.providers.values():
            if hasattr(provider, 'close'):
                await provider.close()


def create_llm_manager(settings: HAINetSettings) -> LLMManager:
    """
    Create and configure constitutional LLM manager
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured LLMManager instance
    """
    return LLMManager(settings)


if __name__ == "__main__":
    # Test the constitutional LLM system
    import asyncio
    from core.config.settings import HAINetSettings
    
    async def test_llm():
        print("HAI-Net Constitutional LLM Test")
        print("=" * 35)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create LLM manager
        llm_manager = create_llm_manager(settings)
        
        try:
            # Initialize LLM manager
            if await llm_manager.initialize():
                print("✅ LLM manager initialized successfully")
                
                # Get available models
                models = llm_manager.get_available_models()
                print(f"📋 Available models: {len(models)}")
                for model in models:
                    print(f"   - {model.name} ({model.provider.value})")
                
                if models:
                    # Test generation
                    test_messages = [
                        LLMMessage(
                            role="user",
                            content="Hello! Can you explain what constitutional AI means?",
                            timestamp=time.time()
                        )
                    ]
                    
                    response = await llm_manager.generate_response(
                        messages=test_messages,
                        model=models[0].name,
                        user_did="did:hai:test_user"
                    )
                    
                    print(f"🤖 AI Response: {response.content[:100]}...")
                    print(f"   Constitutional compliant: {response.constitutional_compliant}")
                    print(f"   Privacy protected: {response.privacy_protected}")
                    print(f"   Tokens used: {response.tokens_used}")
                    print(f"   Response time: {response.response_time_ms:.2f}ms")
                
                # Test usage stats
                stats = llm_manager.get_usage_stats()
                print(f"📊 Usage stats: {stats}")
                
                print("\n🎉 Constitutional LLM System Working!")
                
            else:
                print("❌ Failed to initialize LLM manager")
                
        except Exception as e:
            print(f"❌ LLM test failed: {e}")
        
        finally:
            await llm_manager.close()
    
    # Run the test
    asyncio.run(test_llm())
