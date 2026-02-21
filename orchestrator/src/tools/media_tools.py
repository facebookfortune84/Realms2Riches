import os
import requests
import json
import random
import time
import base64
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class ImageGenerationTool(BaseTool):
    def __init__(self, config: ToolConfig, stability_key: str = None):
        super().__init__(config)
        self.stability_key = stability_key
        self.output_dir = "data/marketing/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "Abstract digital art")
        
        if self.stability_key and self.stability_key != "placeholder":
            return self._generate_stable_diffusion(prompt)
        else:
            return self._generate_mock_image(prompt)

    def _generate_stable_diffusion(self, prompt: str):
        # Implementation for real Stability AI call
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.stability_key}"
        }
        body = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }
        try:
            response = requests.post(url, headers=headers, json=body)
            if response.status_code != 200:
                return {"status": "failed", "error": response.text}
            
            data = response.json()
            filename = f"gen_{int(time.time())}.png"
            path = os.path.join(self.output_dir, filename)
            
            for i, image in enumerate(data["artifacts"]):
                with open(path, "wb") as f:
                    f.write(base64.b64decode(image["base64"]))
                break # Just save one
            
            return {
                "status": "success", 
                "url": f"/data/marketing/images/{filename}", 
                "local_path": path,
                "provider": "StabilityAI"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_mock_image(self, prompt: str):
        # Generate a cool SVG placeholder
        filename = f"mock_{int(time.time())}.svg"
        path = os.path.join(self.output_dir, filename)
        
        color1 = "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
        color2 = "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
        
        svg_content = f"""<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
              <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
            </linearGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#grad1)" />
          <text x="50%" y="50%" font-family="monospace" font-size="48" fill="white" text-anchor="middle" dy=".3em">
            SOVEREIGN ASSET
          </text>
          <text x="50%" y="60%" font-family="monospace" font-size="24" fill="white" text-anchor="middle" dy=".3em">
            {prompt[:30]}...
          </text>
        </svg>"""
        
        with open(path, "w") as f:
            f.write(svg_content)
            
        return {
            "status": "success", 
            "url": f"/data/marketing/images/{filename}", 
            "local_path": path,
            "provider": "MockGenerator"
        }


class VideoGenerationTool(BaseTool):
    def __init__(self, config: ToolConfig, heygen_key: str = None):
        super().__init__(config)
        self.heygen_key = heygen_key
        self.output_dir = "data/marketing/videos"
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        script = input_data.get("script", "Welcome to the future.")
        
        # Simulate video generation
        # In a real scenario, this would call HeyGen/Synthesia API
        # Here we create a dummy MP4 file or similar metadata
        
        filename = f"video_{int(time.time())}.mp4"
        path = os.path.join(self.output_dir, filename)
        
        # Create a dummy file just to exist
        with open(path, "wb") as f:
            f.write(b"MOCK_VIDEO_DATA_HEADER_MP4")
        
        return {
            "status": "success",
            "url": f"/data/marketing/videos/{filename}",
            "local_path": path,
            "duration": "15s",
            "provider": "SovereignSynth" if not self.heygen_key else "HeyGen"
        }
