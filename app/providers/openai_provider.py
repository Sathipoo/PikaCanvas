import openai
import requests
from typing import List
from .base import BaseImageProvider, ImageGenerationRequest, ImageGenerationResponse

class OpenAIProvider(BaseImageProvider):
    """OpenAI DALL-E image generation provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = openai.OpenAI(api_key=api_key)
        self.provider_name = "openai"
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using OpenAI DALL-E"""
        try:
            if not self.validate_request(request):
                return ImageGenerationResponse(
                    success=False,
                    error_message="Invalid request parameters"
                )
            
            # Map our standard sizes to OpenAI sizes
            size_mapping = {
                "1024x1024": "1024x1024",
                "1792x1024": "1792x1024", 
                "1024x1792": "1024x1792"
            }
            
            openai_size = size_mapping.get(request.size, "1024x1024")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=request.prompt,
                size=openai_size,
                quality=request.quality,
                n=1  # DALL-E 3 only supports n=1
            )
            
            # Download the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            metadata = {
                "model": "dall-e-3",
                "size": openai_size,
                "quality": request.quality,
                "revised_prompt": response.data[0].revised_prompt
            }
            
            return ImageGenerationResponse(
                success=True,
                image_data=image_response.content,
                metadata=metadata
            )
            
        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error_message=f"OpenAI generation failed: {str(e)}"
            )
    
    def get_available_models(self) -> List[str]:
        """Return available OpenAI models"""
        return ["dall-e-3", "dall-e-2"]
    
    def get_supported_sizes(self) -> List[str]:
        """Return supported image sizes for OpenAI"""
        return ["1024x1024", "1792x1024", "1024x1792"]