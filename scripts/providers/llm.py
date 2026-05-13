"""
LLM Provider abstraction
Supports: Anthropic, OpenAI, Groq, Cerebras, OpenRouter, Together, Ollama, Custom
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseProvider, ProviderConfig
import json


class LLMProvider(BaseProvider):
    """Base LLM provider with chat completion interface"""
    
    @property
    def provider_type(self) -> str:
        return "llm"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Send chat completion request"""
        raise NotImplementedError("Subclasses must implement chat()")
    
    def chat_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get structured JSON output"""
        # Default implementation - subclasses can optimize
        response = self.chat(
            messages=messages,
            system=system,
            **kwargs
        )
        # Try to extract JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in response
            import re
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())
            raise ValueError("Could not parse JSON from response")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.config.api_key)
        except ImportError:
            raise ImportError("Install with: pip install anthropic")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        client = self.get_client()
        
        # Convert messages to Anthropic format
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        response = client.messages.create(
            model=self.config.model or "claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=formatted_messages,
            temperature=temperature,
        )
        
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider (also works with OpenAI-compatible endpoints)"""
    
    def is_available(self) -> bool:
        # API key optional for local endpoints
        return True
    
    def _create_client(self) -> Any:
        try:
            from openai import OpenAI
            kwargs = {}
            if self.config.api_key:
                kwargs["api_key"] = self.config.api_key
            if self.config.api_base:
                kwargs["base_url"] = self.config.api_base
            return OpenAI(**kwargs)
        except ImportError:
            raise ImportError("Install with: pip install openai")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        client = self.get_client()
        
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)
        
        response = client.chat.completions.create(
            model=self.config.model or "gpt-4o",
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content


class GroqProvider(LLMProvider):
    """Groq provider (fast inference)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        try:
            from groq import Groq
            return Groq(api_key=self.config.api_key)
        except ImportError:
            raise ImportError("Install with: pip install groq")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        client = self.get_client()
        
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)
        
        response = client.chat.completions.create(
            model=self.config.model or "llama-3.3-70b-versatile",
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content


class OllamaProvider(LLMProvider):
    """Ollama provider (local/self-hosted, no API key required)"""
    
    def is_available(self) -> bool:
        # Check if Ollama is running
        try:
            import requests
            base = self.config.api_base or "http://localhost:11434"
            response = requests.get(f"{base}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _create_client(self) -> Any:
        # Ollama doesn't need a client library, just use requests
        return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        import requests
        
        base = self.config.api_base or "http://localhost:11434"
        
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)
        
        response = requests.post(
            f"{base}/api/chat",
            json={
                "model": self.config.model or "llama3.2",
                "messages": formatted_messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            },
            timeout=self.config.timeout,
        )
        
        response.raise_for_status()
        return response.json()["message"]["content"]


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider (aggregator for many models)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        try:
            from openai import OpenAI
            return OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.config.api_key,
            )
        except ImportError:
            raise ImportError("Install with: pip install openai")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        client = self.get_client()
        
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)
        
        extra_headers = {}
        if self.config.extra.get("site_url"):
            extra_headers["HTTP-Referer"] = self.config.extra["site_url"]
        if self.config.extra.get("app_name"):
            extra_headers["X-Title"] = self.config.extra["app_name"]
        
        response = client.chat.completions.create(
            model=self.config.model or "anthropic/claude-sonnet-4",
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers if extra_headers else None,
        )
        
        return response.choices[0].message.content


# Provider registry
LLM_PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
    "cerebras": OpenAIProvider,  # OpenAI-compatible
    "together": OpenAIProvider,  # OpenAI-compatible
    "custom": OpenAIProvider,    # OpenAI-compatible
}


def get_llm_provider(provider_name: str = None, config: Dict = None) -> LLMProvider:
    """Get LLM provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    llm_config = config.get("llm", {})
    
    if provider_name is None:
        provider_name = llm_config.get("active_provider", "anthropic")
    
    providers_config = llm_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = LLM_PROVIDERS.get(provider_name, OpenAIProvider)
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
