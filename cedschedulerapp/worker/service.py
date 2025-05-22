import psutil

from cedschedulerapp.worker.args import server_config
from cedschedulerapp.worker.enums import NodeType
from cedschedulerapp.worker.enums import RegionType
from cedschedulerapp.worker.schemas import NodeResourceStats
from cedschedulerapp.worker.utils import get_gpu_info
from cedschedulerapp.worker.utils import get_node_ip


def get_node_stats() -> NodeResourceStats:
    try:
        # Get system information
        cpu_count = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Get GPU information
        gpu_info = get_gpu_info()
        gpu_count = len(gpu_info)

        # Calculate used resources
        used_cpu_count = int(psutil.cpu_percent() * cpu_count / 100)
        used_memory_count = int(memory.used / (1024 * 1024 * 1024))  # Convert to GB
        used_storage_count = int(disk.used / (1024 * 1024 * 1024))  # Convert to GB

        # Calculate used GPU count based on memory usage and utilization
        used_gpu_count = sum(
            1
            for gpu in gpu_info
            if (gpu.gpu_memory_used / gpu.gpu_memory_total * 100 > 20) or (gpu.gpu_utilization > 20)
        )

        # Get node IP
        node_ip = get_node_ip()

        return NodeResourceStats(
            node_id=server_config.node_id,
            node_ip=node_ip,
            region=RegionType(server_config.region),
            node_type=NodeType(server_config.node_type),
            cpu_count=cpu_count,
            gpu_count=gpu_count,
            memory_count=int(memory.total / (1024 * 1024 * 1024)),  # Convert to GB
            storage_count=int(disk.total / (1024 * 1024 * 1024)),  # Convert to GB
            used_cpu_count=used_cpu_count,
            used_gpu_count=used_gpu_count,
            used_memory_count=used_memory_count,
            used_storage_count=used_storage_count,
            gpu_info=gpu_info,
        )
    except Exception as err:
        raise RuntimeError("Failed to get node statistics") from err
