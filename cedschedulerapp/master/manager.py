from asyncio import Lock

from cedschedulerapp.master.schemas import InferenceService
from cedschedulerapp.master.schemas import NodeResourceStats
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


global_manager: Manager = Manager()
