from typing import Optional

from pydantic import BaseModel


class TextToImage(BaseModel):
    prompt: str
    negative_prompt: str
    height: Optional[int] = 1024
    width: Optional[int] = 1024
    num_inference_steps: Optional[int] = 30
    seed: Optional[int] = -1 
    batch_size: Optional[int] = 1
    refiner: Optional[bool] = False

class ImageToImage(BaseModel):
    image: str
    negative_prompt: str
    prompt: str
    height: Optional[int] = 1024
    width: Optional[int] = 1024
    strength: Optional[int] = 1
    seed: Optional[int] = -1 
    batch_size: Optional[int] = 1
