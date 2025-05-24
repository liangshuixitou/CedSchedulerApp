import asyncio
import random
import string
import time
from asyncio import Lock
from datetime import datetime

from cedschedulerapp.master.args import server_config
from cedschedulerapp.master.client.inference_client import InferenceServerClient
from cedschedulerapp.master.client.training_client import TraingingServerClient
from cedschedulerapp.master.client.types import InferenceInstanceInfo
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
from cedschedulerapp.master.schemas import TaskWrapRuntimeInfo
from cedschedulerapp.master.schemas import TrainingTask
from cedschedulerapp.master.schemas import TrainingTaskDetail
from cedschedulerapp.utils.logger import setup_logger


class Manager:
    def __init__(self):
        self.node_stats: dict[str, NodeResourceStats] = {}
        self.node_stats_lock = Lock()

        self.training_tasks: list[TrainingTaskDetail] = []
        self.inference_services: list[InferenceInstanceInfo] = []
        self.training_client = TraingingServerClient(ip=server_config.training_host, port=server_config.training_port)
        self.inference_client = InferenceServerClient(
            ip=server_config.inference_host, port=server_config.inference_port
        )
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
            )

    async def get_training_task_sim_list(self) -> list[TrainingTask]:
        training_task_list = await self.get_training_task_list()
        sim_list = [TrainingTask.from_training_task_detail(task) for task in training_task_list]
        return sim_list

    async def get_service_sim_list(self) -> list[InferenceService]:
        service_list = await self.get_inference_instance_list()
        sim_list = [InferenceService.from_inference_instance_info(service) for service in service_list]
        return sim_list

    async def get_training_task_list(self) -> list[TrainingTaskDetail]:
        training_task_wrap_runtime_list = await self.training_client.list_tasks()
        self.logger.info(training_task_wrap_runtime_list)
        training_task_list = []
        for task_info in training_task_wrap_runtime_list:
            task_meta = TaskMeta(**task_info.get("task_meta", {}))

            task_wrap = TaskWrapRuntimeInfo(
                task_meta=task_meta,
                schedule_infos=task_info.get("schedule_infos", {}),
                inst_status=task_info.get("inst_status", {}),
                inst_data_status=task_info.get("inst_data_status", {}),
                task_submit_time=task_info.get("task_submit_time", 0.0),
                task_start_time=task_info.get("task_start_time", 0.0),
                task_end_time=task_info.get("task_end_time", 0.0),
            )

            task_detail = TrainingTaskDetail(
                task_id=task_meta.task_id,
                task_name=task_meta.task_name,
                task_inst_num=task_meta.task_inst_num,
                task_plan_cpu=task_meta.task_plan_cpu,
                task_plan_mem=task_meta.task_plan_mem,
                task_plan_gpu=task_meta.task_plan_gpu,
                task_status=task_meta.task_status,
                schedule_infos=task_wrap.schedule_infos,
                inst_status=task_wrap.inst_status,
                task_submit_time=task_wrap.task_submit_time,
                task_start_time=task_wrap.task_start_time,
                task_end_time=task_wrap.task_end_time,
            )
            training_task_list.append(task_detail)
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
        task_log = await self.training_client.get_training_task_log(task_id)
        self.logger.info(task_log)
        return TaskLogResponse(task_id=task_id, logs=task_log)

    async def get_inference_instance_list(self) -> list[InferenceInstanceInfo]:
        instances = await self.inference_client.list_instances()
        self.logger.info(instances)
        self.inference_services = instances
        return instances

    async def get_inference_instance_log(self, instance_id: str) -> str:
        log = await self.inference_client.get_instance_log(instance_id)
        self.logger.info(log)
        return log

    async def generate(self, prompt: str) -> str:
        response = await self.inference_client.generate(prompt)
        response = response["text"][0] if isinstance(response, dict) and "text" in response else response
        return response


global_manager: Manager = Manager()
