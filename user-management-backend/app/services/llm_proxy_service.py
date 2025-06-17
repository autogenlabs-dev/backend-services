"""LLM proxy service for token-gated provider access."""

import httpx
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User, TokenUsageLog
from .token_service import TokenService, TokenPricingService


class LLMProviderClient:
    """Base class for LLM provider clients."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from the provider."""
        raise NotImplementedError
    
    async def chat_completion(self, messages: List[Dict[str, Any]], model: str, **kwargs) -> Dict[str, Any]:
        """Create a chat completion."""
        raise NotImplementedError
    
    async def text_completion(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Create a text completion."""
        raise NotImplementedError
    
    async def embeddings(self, input_text: str, model: str, **kwargs) -> Dict[str, Any]:
        """Create embeddings."""
        raise NotImplementedError


class OpenRouterClient(LLMProviderClient):
    """OpenRouter API client."""
    
    def __init__(self):
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List OpenRouter models."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return [{
                "id": model["id"],
                "name": model["name"],
                "provider": "openrouter",
                "context_length": model.get("context_length", 4096),
                "pricing": model.get("pricing", {}),
                "description": model.get("description", "")
            } for model in data.get("data", [])]
            
        except Exception as e:
            return [{"error": f"Failed to fetch OpenRouter models: {str(e)}"}]
    
    async def chat_completion(self, messages: List[Dict[str, Any]], model: str, **kwargs) -> Dict[str, Any]:
        """Create OpenRouter chat completion."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {"error": f"OpenRouter chat completion failed: {str(e)}"}


class GlamaClient(LLMProviderClient):
    """Glama API client."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.glama.ai/v1",
            api_key=settings.glama_api_key
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List Glama models."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return [{
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "provider": "glama",
                "context_length": model.get("context_length", 4096),
                "description": model.get("description", "")
            } for model in data.get("data", [])]
            
        except Exception as e:
            return [{"error": f"Failed to fetch Glama models: {str(e)}"}]


class RequestyClient(LLMProviderClient):
    """Requesty API client."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.requesty.ai/v1",
            api_key=settings.requesty_api_key
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List Requesty models."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return [{
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "provider": "requesty",
                "context_length": model.get("context_length", 4096),
                "description": model.get("description", "")
            } for model in data.get("data", [])]
            
        except Exception as e:
            return [{"error": f"Failed to fetch Requesty models: {str(e)}"}]


class AIMLClient(LLMProviderClient):
    """AIML API client."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.aimlapi.com/v1",
            api_key=settings.aiml_api_key
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List AIML models."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return [{
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "provider": "aiml",
                "context_length": model.get("context_length", 4096),
                "description": model.get("description", "")
            } for model in data.get("data", [])]
            
        except Exception as e:
            return [{"error": f"Failed to fetch AIML models: {str(e)}"}]


class A4FClient(LLMProviderClient):
    """A4F (AI for Fun) API client."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.a4f.co/v1",
            api_key=settings.a4f_api_key
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List A4F models."""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=2.0
            )
            response.raise_for_status()
            data = response.json()
            
            return [{
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "provider": "a4f",
                "context_length": model.get("context_length", model.get("max_tokens", 4096)),
                "description": model.get("description", ""),
                "pricing": model.get("pricing", {}),
                "capabilities": model.get("capabilities", [])
            } for model in data.get("data", [])]
            
        except Exception as e:
            return [{"error": f"Failed to fetch A4F models: {str(e)}"}]
    
    async def chat_completion(self, messages: List[Dict[str, Any]], model: str, **kwargs) -> Dict[str, Any]:
        """Create A4F chat completion."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "stream": kwargs.get("stream", False),
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {"error": f"A4F chat completion failed: {str(e)}"}


class LLMProxyService:
    """Service for proxying LLM requests with token management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.token_service = TokenService(db)
        self.pricing_service = TokenPricingService()
        
        # Initialize provider clients
        self.providers = {
            "openrouter": OpenRouterClient(),
            "glama": GlamaClient(),        "requesty": RequestyClient(),
            "aiml": AIMLClient(),
            "a4f": A4FClient()
        }
        
        # Simple cache for models with 60-second TTL
        self._models_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 60  # 60 seconds
    
    async def close(self):
        """Close all provider clients."""
        for provider in self.providers.values():
            await provider.close()
    
    def get_provider_from_model(self, model: str) -> Tuple[str, LLMProviderClient]:
        """Determine provider from model name with A4F prioritization for popular models."""
        # First check for explicit provider prefixes
        if "openrouter" in model.lower() or model.startswith("or/"):
            return "openrouter", self.providers["openrouter"]
        elif "glama" in model.lower() or model.startswith("glama/"):
            return "glama", self.providers["glama"]
        elif "requesty" in model.lower() or model.startswith("req/"):
            return "requesty", self.providers["requesty"]
        elif "aiml" in model.lower() or model.startswith("aiml/"):
            return "aiml", self.providers["aiml"]
        elif "a4f" in model.lower() or model.startswith("a4f/"):
            return "a4f", self.providers["a4f"]
        
        # Prioritize A4F for popular models (GPT, Claude, Gemini)
        model_lower = model.lower()
        if any(popular in model_lower for popular in ["gpt", "claude", "gemini", "sonnet", "haiku", "opus"]):
            return "a4f", self.providers["a4f"]
        
        # Default to OpenRouter for other models
        return "openrouter", self.providers["openrouter"]
    
    async def list_all_models(self) -> Dict[str, Any]:
        """List models from all providers with concurrent requests, aggressive timeout, and caching."""
        current_time = time.time()
        
        # Check if we have a valid cache
        if (self._models_cache is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._models_cache
        
        all_models = []
        provider_status = {}
        
        # Create tasks for concurrent execution with individual timeouts
        async def fetch_provider_models(provider_name: str, client: LLMProviderClient):
            try:
                # Set individual timeout per provider to 0.3 seconds for ultra-fast response
                models = await asyncio.wait_for(client.list_models(), timeout=0.3)
                return provider_name, models, "available"
            except asyncio.TimeoutError:
                return provider_name, [], "timeout"
            except Exception as e:
                return provider_name, [], f"error: {str(e)}"
        
        # Execute all requests concurrently with aggressive timeout
        tasks = [
            fetch_provider_models(name, client) 
            for name, client in self.providers.items()
        ]
        
        try:
            # Wait for all tasks with a 1.0-second global timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), 
                timeout=1.0
            )
            
            for result in results:
                if isinstance(result, Exception):
                    continue
                provider_name, models, status = result
                if models:  # Only add non-empty model lists
                    all_models.extend(models)
                provider_status[provider_name] = status
                
        except asyncio.TimeoutError:
            # Fallback to cached models if all providers are slow
            provider_status = {name: "timeout" for name in self.providers.keys()}
        
        # If no models were fetched, return fallback models
        if not all_models:
            all_models = [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "cached",
                    "description": "Cached model (providers unavailable)"
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4", 
                    "provider": "cached",
                    "description": "Cached model (providers unavailable)"
                },
                {
                    "id": "claude-3-sonnet",
                    "name": "Claude 3 Sonnet",
                    "provider": "cached", 
                    "description": "Cached model (providers unavailable)"
                }
            ]
            if not provider_status:
                provider_status = {name: "fallback" for name in self.providers.keys()}
        
        result = {
            "models": all_models,
            "provider_status": provider_status,
            "total_models": len(all_models)
        }
        
        # Cache the result
        self._models_cache = result
        self._cache_timestamp = current_time
        
        return result
    
    async def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple approximation: ~4 characters per token
        return max(1, len(text) // 4)
    
    async def chat_completion(self, user: User, messages: List[Dict[str, Any]], model: str, **kwargs) -> Dict[str, Any]:
        """Process chat completion with token management."""
        try:
            # Estimate tokens needed
            total_text = " ".join([msg.get("content", "") for msg in messages])
            estimated_tokens = await self.estimate_tokens(total_text, model)
            
            # Check if user has sufficient tokens
            if not self.token_service.can_use_tokens(user, estimated_tokens):
                return {
                    "error": "Insufficient tokens",
                    "details": "Your current plan doesn't have enough tokens for this request",
                    "required_tokens": estimated_tokens,
                    "available_tokens": self.token_service.get_available_tokens(user)
                }
            
            # Reserve tokens
            reservation_id = self.token_service.reserve_tokens(user, estimated_tokens, "chat_completion", {
                "model": model,
                "message_count": len(messages)
            })
            
            try:
                # Route to appropriate provider
                provider_name, provider_client = self.get_provider_from_model(model)
                
                # Make the API call
                response = await provider_client.chat_completion(messages, model, **kwargs)
                
                if "error" in response:
                    # Release reserved tokens on error
                    self.token_service.release_reserved_tokens(reservation_id)
                    return response
                
                # Calculate actual tokens used
                actual_tokens = response.get("usage", {}).get("total_tokens", estimated_tokens)
                cost = self.pricing_service.calculate_cost(provider_name, model, actual_tokens, "chat")
                
                # Consume tokens and log usage
                self.token_service.consume_reserved_tokens(
                    reservation_id=reservation_id,
                    actual_tokens=actual_tokens,
                    cost_usd=cost,
                    response_metadata={
                        "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
                        "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0)
                    }
                )
                
                # Add usage info to response
                response["_usage_info"] = {
                    "tokens_used": actual_tokens,
                    "cost_usd": float(cost),
                    "provider": provider_name,
                    "remaining_tokens": self.token_service.get_available_tokens(user)
                }
                
                return response
                
            except Exception as e:
                # Release reserved tokens on error
                self.token_service.release_reserved_tokens(reservation_id)
                return {"error": f"Request failed: {str(e)}"}
        
        except Exception as e:
            return {"error": f"Token management error: {str(e)}"}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        return {
            "providers": list(self.providers.keys()),
            "status": "All providers initialized",
            "supported_operations": ["chat_completion", "text_completion", "embeddings", "list_models"]
        }