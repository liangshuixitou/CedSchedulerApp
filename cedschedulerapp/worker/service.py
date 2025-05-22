import psutil
from .types import NodeResourceStatsResponse, RegionType, NodeType
from .utils import get_gpu_info, get_node_ip

def get_node_stats() -> NodeResourceStatsResponse:
    try:
        # Get system information
        cpu_count = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get GPU information
        gpu_info = get_gpu_info()
        gpu_count = len(gpu_info)
        
        # Calculate used resources
        used_cpu_count = int(psutil.cpu_percent() * cpu_count / 100)
        used_memory_count = int(memory.used / (1024 * 1024 * 1024))  # Convert to GB
        used_storage_count = int(disk.used / (1024 * 1024 * 1024))  # Convert to GB
        
        # Get node IP
        hostname = psutil.Process().name()
        node_ip = get_node_ip()
        
        return NodeResourceStatsResponse(
            node_id=hostname,
            node_ip=node_ip,
            region=RegionType.Cloud,  # This should be configured based on deployment
            node_type=NodeType.Training,  # This should be configured based on deployment
            cpu_count=cpu_count,
            gpu_count=gpu_count,
            memory_count=int(memory.total / (1024 * 1024 * 1024)),  # Convert to GB
            storage_count=int(disk.total / (1024 * 1024 * 1024)),  # Convert to GB
            used_cpu_count=used_cpu_count,
            used_gpu_count=gpu_count,  # Assuming all GPUs are used if present
            used_memory_count=used_memory_count,
            used_storage_count=used_storage_count,
            gpu_info=gpu_info
        )
    except Exception as err:
        raise RuntimeError("Failed to get node statistics") from err 