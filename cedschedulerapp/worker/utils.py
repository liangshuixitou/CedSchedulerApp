import socket
import GPUtil
from typing import List
from .types import GPUInfo

def get_gpu_info() -> List[GPUInfo]:
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("No NVIDIA GPUs found on this system")
            return []
        return [
            GPUInfo(
                gpu_id=str(gpu.id),
                gpu_type=gpu.name,
                gpu_memory_total=int(gpu.memoryTotal),
                gpu_memory_used=int(gpu.memoryUsed),
                gpu_utilization=float(gpu.load * 100)
            )
            for gpu in gpus
        ]
    except ImportError as err:
        print("GPUtil is not installed. Please install it using: pip install gputil")
        raise ImportError("GPUtil is not installed") from err
    except Exception as err:
        print(f"Error getting GPU info: {err}")
        raise RuntimeError("Failed to get GPU information") from err

def get_node_ip() -> str:
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as err:
        raise RuntimeError("Failed to get node IP address") from err 