from typing import Dict, Type, List
from .base import BaseImageProvider
from .openai_provider import OpenAIProvider
from .stability_provider import StabilityProvider

class ProviderFactory:
    """Factory class to create image generation providers"""
    
    _providers: Dict[str, Type[BaseImageProvider]] = {
        "openai": OpenAIProvider,
        "stability": StabilityProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: str) -> BaseImageProvider:
        """Create a provider instance"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseImageProvider]):
        """Register a new provider"""
        cls._providers[name] = provider_class