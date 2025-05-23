import asyncio
import random
import string
import time
from asyncio import Lock
from datetime import datetime

from cedschedulerapp.master.args import server_config
from cedschedulerapp.master.client.training_client import TraingingServerClient
from cedschedulerapp.master.client.types import TaskMeta
from cedschedulerapp.master.enums import GPUPerformance
from cedschedulerapp.master.enums import GPUType
from cedschedulerapp.master.enums import RegionType
from cedschedulerapp.master.enums import TaskStatus
from cedschedulerapp.master.schemas import InferenceService
from cedschedulerapp.master.schemas import NodeResourceStats
from cedschedulerapp.master.schemas import ResourceStats
from cedschedulerapp.master.schemas import SubmitTaskRequest
from cedschedulerapp.master.schemas import TaskLogResponse
from cedschedulerapp.master.schemas import TrainingTask
from cedschedulerapp.master.schemas import TrainingTaskDetail
from cedschedulerapp.utils.logger import setup_logger


class Manager:
    def __init__(self):
        self.node_stats: dict[str, NodeResourceStats] = {}
        self.node_stats_lock = Lock()

        self.training_tasks: list[TrainingTaskDetail] = []
        self.inference_services: list[InferenceService] = []
        self.training_client = TraingingServerClient(ip=server_config.training_host, port=server_config.training_port)
        self.logger = setup_logger(__name__)
        self.get_training_task_list_daemon()

    def get_training_task_list_daemon(self):
        async def _daemon():
            while True:
                try:
                    await self.get_training_task_list()
                except Exception as e:
                    self.logger.error(f"Error in training task list daemon: {e}")
                await asyncio.sleep(5)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(_daemon())

    async def update_node_stats(self, node_id: str, node_stats: NodeResourceStats):
        async with self.node_stats_lock:
            self.node_stats[node_id] = node_stats

    async def get_node_stats(self, node_id: str) -> NodeResourceStats:
        async with self.node_stats_lock:
            return self.node_stats[node_id]

    async def get_all_node_stats(self) -> list[NodeResourceStats]:
        async with self.node_stats_lock:
            return list(self.node_stats.values())

    async def get_nodes_stats_by_region(self, region: RegionType) -> list[NodeResourceStats]:
        async with self.node_stats_lock:
            return [node for node in self.node_stats.values() if node.region == region]

    async def get_resource_stats(self) -> ResourceStats:
        async with self.node_stats_lock:
            return ResourceStats(
                cloud_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.Cloud),
                edge_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.Edge),
                device_node_count=sum(1 for node in self.node_stats.values() if node.region == RegionType.Device),
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
                training_tasks=[TrainingTask.from_training_task_detail(task) for task in self.training_tasks],
                inference_services=self.inference_services,
            )

    async def get_training_task_list(self) -> list[TrainingTask]:
        training_task_wrap_runtime_list = await self.training_client.list_tasks()
        self.logger.info(training_task_wrap_runtime_list)
        training_task_list = []
        for task_info in training_task_wrap_runtime_list:
            task_detail = TrainingTaskDetail(
                task_id=task_info.get("task_id", ""),
                task_name=task_info.get("task_name", ""),
                task_inst_num=task_info.get("task_inst_num", 0),
                task_plan_cpu=task_info.get("task_plan_cpu", 0.0),
                task_plan_mem=task_info.get("task_plan_mem", 0.0),
                task_plan_gpu=task_info.get("task_plan_gpu", 0),
                task_status=task_info.get("task_status", TaskStatus.Submitted),
                schedule_infos=task_info.get("schedule_infos", {}),
                inst_status=task_info.get("inst_status", {}),
                task_submit_time=task_info.get("task_submit_time", 0.0),
                task_start_time=task_info.get("task_start_time", 0.0),
                task_end_time=task_info.get("task_end_time", 0.0),
            )
            training_task_list.append(TrainingTask.from_training_task_detail(task_detail))
        self.training_tasks = training_task_list
        return training_task_list

    async def submit_task(self, request: list[SubmitTaskRequest]):
        for task_request in request:
            # Generate random string (4 characters)
            random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

            # Convert SubmitTaskRequest to TaskMeta
            task_meta = TaskMeta(
                task_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{random_str}",
                task_name=task_request.task_name,
                task_inst_num=task_request.inst_num,
                task_plan_cpu=float(task_request.plan_cpu),
                task_plan_mem=float(task_request.plan_mem),
                task_plan_gpu=task_request.plan_gpu,
                task_status=TaskStatus.Submitted,
                task_start_time=time.time(),
                task_runtime={
                    GPUType.V100: int(
                        task_request.runtime * GPUPerformance.T4_PERFORMANCE / GPUPerformance.V100_PERFORMANCE
                    ),
                    GPUType.P100: int(
                        task_request.runtime * GPUPerformance.T4_PERFORMANCE / GPUPerformance.P100_PERFORMANCE
                    ),
                    GPUType.T4: int(task_request.runtime),
                },
            )

            self.logger.info(task_meta)
            # Submit task using training client
            await self.training_client.submit_task(task_meta)

            # Wait for 3 seconds before submitting next task
            await asyncio.sleep(3)

    async def get_training_task_log(self, task_id: str) -> TaskLogResponse:
        return await self.training_client.get_training_task_log(task_id)


global_manager: Manager = Manager()
