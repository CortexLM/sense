from schemas.system import SystemInfo, GPUInfo
import psutil
import GPUtil

import psutil
import GPUtil
from typing import List, Optional

def get_system_info() -> SystemInfo:
    """
    Retrieves and returns system information including details about the CPU, memory, and GPUs.

    Returns:
        SystemInfo: An object containing:
            - cpu_cores (int): The total number of logical CPU cores.
            - cpu_utilization (float): The current CPU utilization percentage.
            - total_memory (float): The total system memory in gigabytes (GB).
            - available_memory (float): The available system memory in gigabytes (GB).
            - gpus (Optional[List[GPUInfo]]): A list of GPUInfo objects each containing details about a GPU, if any are present.
    """
    # CPU information
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_utilization = psutil.cpu_percent()

    # Memory information
    mem = psutil.virtual_memory()
    total_memory_gb = mem.total / (1024**3)  # Convert to GB
    available_memory_gb = mem.available / (1024**3)  # Convert to GB

    # GPU information
    gpus = []
    for gpu in GPUtil.getGPUs():
        gpus.append(GPUInfo(
            name=gpu.name,
            total_memory=int(gpu.memoryTotal),
            used_memory=int(gpu.memoryUsed),
            utilization=float(gpu.load * 100),
            uuid=gpu.uuid
        ))

    return SystemInfo(
        cpu_cores=cpu_cores,
        cpu_utilization=float(cpu_utilization),
        total_memory=float(total_memory_gb),
        available_memory=float(available_memory_gb),
        gpus=gpus if gpus else None
    )