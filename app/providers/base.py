from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ImageGenerationRequest:
    prompt: str
    size: str = "1024x1024"
    style: Optional[str] = None
    count: int = 1
    quality: str = "standard"

@dataclass
class ImageGenerationResponse:
    success: bool
    image_data: Optional[bytes] = None
    filename: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class BaseImageProvider(ABC):
    """Abstract base class for all image generation providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')
    
    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate an image based on the request parameters"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider"""
        pass
    
    @abstractmethod
    def get_supported_sizes(self) -> List[str]:
        """Return list of supported image sizes"""
        pass
    
    def validate_request(self, request: ImageGenerationRequest) -> bool:
        """Validate the generation request"""
        if not request.prompt or len(request.prompt.strip()) == 0:
            return False
        if request.size not in self.get_supported_sizes():
            return False
        return True