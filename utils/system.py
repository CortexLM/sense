# For GPU information, we will use the GPUtil library. 
# This requires the library to be installed. If not installed, we handle the import error.
import os
import platform
import sys
import psutil
from utils.logging import logging
import GPUtil
import uuid    

def terminate_all_process():
    try:
        logging.info("The daemon waits until all processes have finished to free up resources.")
        current_process = psutil.Process()
        for child in current_process.children(recursive=True):
            child.terminate()
        sys.exit(0)  
    except SystemExit:
        pass
def get_gpu_info():
    """
    Get the GPU information if GPUtil is available. Filters GPUs based on CUDA_VISIBLE_DEVICES.
    """
    # Retrieve the list of all GPUs
    all_gpus = GPUtil.getGPUs()

    # Check if CUDA_VISIBLE_DEVICES is set and parse it
    cuda_visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
    if cuda_visible_devices:
        available_gpu_ids = [int(id) for id in cuda_visible_devices.split(',')]
        # Filter to get only those GPUs that are visible as per CUDA_VISIBLE_DEVICES
        available_gpus = [gpu for gpu in all_gpus if gpu.id in available_gpu_ids]
    else:
        # If CUDA_VISIBLE_DEVICES is not set, consider all GPUs as available
        available_gpus = all_gpus

    return [{"uuid": gpu.uuid, "name": gpu.name, "total_memory": f"{gpu.memoryTotal}", "free_memory": gpu.memoryFree, "memory_used": gpu.memoryUsed, "driver": gpu.driver, "load": gpu.load  } for gpu in available_gpus]

def display_system_info():
    logging.info("Gathering system information...")
    info = {
        "Operating System": platform.system(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": sys.version,
        "Total RAM": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "GPUs": get_gpu_info()
    }
    
    for key, value in info.items():
        logging.info(f"{key}: {value}")

def read_cgroup_file(file_path):
    """
    Reads a value from a cgroup file and returns it.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        return 0

def is_running_in_docker():
    """
    Check if the script is running in a Docker container.
    """
    return os.path.exists('/.dockerenv')

def get_all_system_info():
    """
    Gather and return all system information in JSON format, including cgroup-specific 
    memory and CPU data.
    """
    try:
        system_info = {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": sys.version,
            "total_ram": psutil.virtual_memory().total / (1024 ** 2),
            "free_ram": psutil.virtual_memory().available / (1024 ** 2),
            "disk_space": {
                "total": psutil.disk_usage('/').total / (1024 ** 2),
                "used": psutil.disk_usage('/').used / (1024 ** 2),
                "free": psutil.disk_usage('/').free / (1024 ** 2)
            },
            "gpus": get_gpu_info()
        }
        if is_running_in_docker():
            system_info["docker"] = {
                "cgroup_memory_usage": read_cgroup_file('/sys/fs/cgroup/memory/memory.usage_in_bytes'),
                "cgroup_memory_limit": read_cgroup_file('/sys/fs/cgroup/memory/memory.limit_in_bytes'),
                "cgroup_cpu_quota": read_cgroup_file('/sys/fs/cgroup/cpu/cpu.cfs_quota_us'),
                "cgroup_cpu_period": read_cgroup_file('/sys/fs/cgroup/cpu/cpu.cfs_period_us'),
                "cgroup_cpu_usage": read_cgroup_file('/sys/fs/cgroup/cpu/cpuacct.usage')
            }

        return system_info
    except Exception as e:
        logging.error(f"Error in gathering system info: {e}")
        return {"error": str(e)}