import requests
import base64
from typing import List
from .base import BaseImageProvider, ImageGenerationRequest, ImageGenerationResponse

class StabilityProvider(BaseImageProvider):
    """Stability AI image generation provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.stability.ai"
        self.provider_name = "stability"
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using Stability AI"""
        try:
            if not self.validate_request(request):
                return ImageGenerationResponse(
                    success=False,
                    error_message="Invalid request parameters"
                )
            
            # Parse dimensions
            width, height = map(int, request.size.split('x'))
            
            # Prepare the request
            url = f"{self.base_url}/v1/generation/stable-diffusion-v1-6/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            body = {
                "text_prompts": [
                    {
                        "text": request.prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30
            }
            
            if request.style:
                body["style_preset"] = request.style
            
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            data = response.json()
            
            # Decode the base64 image
            image_data = base64.b64decode(data["artifacts"][0]["base64"])
            
            metadata = {
                "model": "stable-diffusion-v1-6",
                "size": request.size,
                "cfg_scale": 7,
                "steps": 30,
                "style": request.style
            }
            
            return ImageGenerationResponse(
                success=True,
                image_data=image_data,
                metadata=metadata
            )
            
        except Exception as e:
            return ImageGenerationResponse(
                success=False,
                error_message=f"Stability AI generation failed: {str(e)}"
            )
    
    def get_available_models(self) -> List[str]:
        """Return available Stability AI models"""
        return ["stable-diffusion-v1-6", "stable-diffusion-xl-1024-v1-0"]
    
    def get_supported_sizes(self) -> List[str]:
        """Return supported image sizes for Stability AI"""
        return ["512x512", "768x768", "1024x1024", "1536x1536"]