from asyncio import Lock

from cedschedulerapp.master.enums import RegionType
from cedschedulerapp.master.schemas import InferenceService
from cedschedulerapp.master.schemas import NodeResourceStats
from cedschedulerapp.master.schemas import ResourceStats
from cedschedulerapp.master.schemas import TrainingTask


class Manager:
    def __init__(self):
        self.node_stats: dict[str, NodeResourceStats] = {}
        self.node_stats_lock = Lock()

        self.training_tasks: list[TrainingTask] = []
        self.inference_services: list[InferenceService] = []

    async def update_node_stats(self, node_id: str, node_stats: NodeResourceStats):
        async with self.node_stats_lock:
            self.node_stats[node_id] = node_stats

    async def get_node_stats(self, node_id: str) -> NodeResourceStats:
        async with self.node_stats_lock:
            return self.node_stats[node_id]

    async def get_all_node_stats(self) -> list[NodeResourceStats]:
        async with self.node_stats_lock:
            return list(self.node_stats.values())

    async def get_resource_stats(self) -> ResourceStats:
        async with self.node_stats_lock:
            return ResourceStats(
                cloud_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.CLOUD),
                edge_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.EDGE),
                device_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.DEVICE),
                total_cpu_count=sum(node.cpu_count for node in self.node_stats.values()),
                used_cpu_count=sum(node.used_cpu_count for node in self.node_stats.values()),
                total_gpu_count=sum(node.gpu_count for node in self.node_stats.values()),
                used_gpu_count=sum(node.used_gpu_count for node in self.node_stats.values()),
                total_memory_count=sum(node.memory_count for node in self.node_stats.values()),
                used_memory_count=sum(node.used_memory_count for node in self.node_stats.values()),
                total_storage_count=sum(node.storage_count for node in self.node_stats.values()),
                used_storage_count=sum(node.used_storage_count for node in self.node_stats.values()),
                training_task_count=len(self.training_tasks),
                inference_service_count=len(self.inference_services),
                training_tasks=self.training_tasks,
                inference_services=self.inference_services,
            )


global_manager: Manager = Manager()
