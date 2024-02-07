from pydantic import BaseModel
from typing import List, Optional

class GPUInfo(BaseModel):
    name: str
    total_memory: int  # Represents total memory in MB
    used_memory: int   # Used memory, also in MB
    utilization: float   # GPU utilization as a percentage
    uuid: str          # Unique UUID to identify the GPU

class SystemInfo(BaseModel):
    cpu_info: str  # This information could be a simple string or a more complex model
    total_memory: str  # Total system memory
    available_memory: str  # Available system memory
    gpus: Optional[List[GPUInfo]] = None  # Optional list of GPUs

