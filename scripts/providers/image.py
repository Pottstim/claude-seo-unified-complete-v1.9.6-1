"""
Image Generation Provider abstraction
Supports: Stable Diffusion (local), ComfyUI, DALL-E, Replicate, HuggingFace, Gemini, Banana
"""

from typing import Any, Dict, Optional
from .base import BaseProvider, ProviderConfig


class ImageProvider(BaseProvider):
    """Base image generation provider"""
    
    @property
    def provider_type(self) -> str:
        return "image"
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, **kwargs) -> Dict[str, Any]:
        """Generate image from prompt"""
        raise NotImplementedError("Subclasses must implement generate()")


class StableDiffusionProvider(ImageProvider):
    """
    Stable Diffusion WebUI provider (self-hosted, open source)
    Requires: AUTOMATIC1111 WebUI running locally
    """
    
    def is_available(self) -> bool:
        import requests
        base = self.config.api_base or "http://localhost:7860"
        try:
            response = requests.get(f"{base}/sdapi/v1/sd-models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _create_client(self) -> Any:
        return None
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, **kwargs) -> Dict[str, Any]:
        """Generate image using Stable Diffusion WebUI API"""
        import requests
        import base64
        
        base = self.config.api_base or "http://localhost:7860"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": kwargs.get("negative_prompt", "blurry, low quality, distorted"),
            "steps": kwargs.get("steps", 30),
            "width": width,
            "height": height,
            "cfg_scale": kwargs.get("cfg_scale", 7),
        }
        
        response = requests.post(f"{base}/sdapi/v1/txt2img", json=payload, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        image_data = base64.b64decode(data["images"][0])
        
        return {
            "image_data": image_data,
            "provider": "stable_diffusion",
            "prompt": prompt,
            "seed": data.get("info", {}).get("seed"),
        }


class DALLEProvider(ImageProvider):
    """OpenAI DALL-E provider"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        from openai import OpenAI
        return OpenAI(api_key=self.config.api_key)
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, **kwargs) -> Dict[str, Any]:
        """Generate image using DALL-E"""
        import requests
        
        client = self.get_client()
        
        # Map size
        size = "1024x1024"
        if width == 1792 or height == 1792:
            size = "1792x1024" if width > height else "1024x1792"
        
        response = client.images.generate(
            model=self.config.model or "dall-e-3",
            prompt=prompt,
            size=size,
            quality=kwargs.get("quality", "standard"),
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download image
        img_response = requests.get(image_url)
        
        return {
            "image_data": img_response.content,
            "image_url": image_url,
            "provider": "dalle",
            "prompt": prompt,
            "revised_prompt": response.data[0].revised_prompt,
        }


class ReplicateProvider(ImageProvider):
    """Replicate provider (hosted open-source models)"""
    
    def is_available(self) -> bool:
        return bool(self.config.api_key)
    
    def _create_client(self) -> Any:
        import replicate
        return replicate
    
    def generate(self, prompt: str, width: int = 1024, height: int = 1024, **kwargs) -> Dict[str, Any]:
        """Generate image using Replicate"""
        import replicate
        import requests
        
        model = self.config.model or "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        
        output = replicate.run(
            model,
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": kwargs.get("steps", 30),
            }
        )
        
        # Download image
        if isinstance(output, list):
            output = output[0]
        
        img_response = requests.get(output)
        
        return {
            "image_data": img_response.content,
            "image_url": output,
            "provider": "replicate",
            "prompt": prompt,
        }


# Provider registry
IMAGE_PROVIDERS = {
    "stable_diffusion": StableDiffusionProvider,
    "comfyui": StableDiffusionProvider,  # Similar API
    "dalle": DALLEProvider,
    "replicate": ReplicateProvider,
    "huggingface": ReplicateProvider,  # Similar usage
}


def get_image_provider(provider_name: str = None, config: Dict = None) -> Optional[ImageProvider]:
    """Get image provider by name or from config"""
    if config is None:
        config = BaseProvider.load_config()
    
    image_config = config.get("image_generation", {})
    
    if provider_name is None:
        provider_name = image_config.get("active_provider")
        if not provider_name:
            return None  # Image generation is optional
    
    providers_config = image_config.get("providers", {})
    provider_config = providers_config.get(provider_name, {})
    
    provider_class = IMAGE_PROVIDERS.get(provider_name)
    if not provider_class:
        return None
    
    return provider_class(ProviderConfig.from_dict(provider_name, provider_config))
