import time
from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel

from cedschedulerapp.master.client.client_type import InferenceInstanceInfo
from cedschedulerapp.master.client.client_type import ScheduleInfo
from cedschedulerapp.master.client.client_type import TaskWrapRuntimeInfo
from cedschedulerapp.master.enums import NodeType
from cedschedulerapp.master.enums import RegionType
from cedschedulerapp.master.enums import TaskInstStatus
from cedschedulerapp.master.enums import TaskStatus

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class GPUInfo(BaseModel):
    gpu_id: str
    gpu_type: str
    gpu_memory_total: int
    gpu_memory_used: int
    gpu_utilization: float


class NodeResourceStats(BaseModel):
    node_id: str
    node_ip: str
    region: RegionType
    node_type: NodeType
    cpu_count: int
    gpu_count: int
    memory_count: int
    storage_count: int
    used_cpu_count: int
    used_gpu_count: int
    used_memory_count: int
    used_storage_count: int
    gpu_info: list[GPUInfo]


class TrainingTaskDetail(BaseModel):
    task_id: str
    task_name: str
    task_inst_num: int
    task_plan_cpu: float
    task_plan_mem: float
    task_plan_gpu: int
    task_status: TaskStatus
    schedule_infos: dict[int, ScheduleInfo]
    inst_status: dict[int, TaskInstStatus]
    task_submit_time: float
    task_start_time: float
    task_end_time: float

    @classmethod
    def from_training_task_wrap_runtime_info(cls, task: TaskWrapRuntimeInfo):
        return cls(
            task_id=task.task_meta.task_id,
            task_name=task.task_meta.task_name,
            task_inst_num=task.task_meta.task_inst_num,
            task_plan_cpu=task.task_meta.task_plan_cpu,
            task_plan_mem=task.task_meta.task_plan_mem,
            task_plan_gpu=task.task_meta.task_plan_gpu,
            task_status=task.task_meta.task_status,
            schedule_infos=task.schedule_infos,
            inst_status=task.inst_status,
            task_submit_time=task.task_submit_time,
            task_start_time=task.task_start_time,
            task_end_time=task.task_end_time,
        )


class TrainingTask(BaseModel):
    id: str
    name: str
    duration: float
    status: TaskStatus

    @classmethod
    def from_training_task_detail(cls, task: TrainingTaskDetail):
        if task.task_end_time < task.task_start_time:
            duration = time.time() - task.task_start_time
        else:
            duration = task.task_end_time - task.task_start_time
        return cls(
            id=task.task_id,
            name=task.task_name,
            duration=duration,
            status=task.task_status,
        )


class InferenceService(BaseModel):
    instance_id: str
    gpu_count: int
    block_count: int
    used_block_count: int

    @classmethod
    def from_inference_instance_info(cls, instance: InferenceInstanceInfo):
        return cls(
            instance_id=instance.instance_id,
            gpu_count=instance.gpu_count,
            block_count=instance.total_gpu_blocks_count,
            used_block_count=instance.used_gpu_blocks_count,
        )


class ResourceStats(BaseModel):
    cloud_node_count: int
    edge_node_count: int
    device_node_count: int
    total_cpu_count: int
    used_cpu_count: int
    total_gpu_count: int
    used_gpu_count: int
    total_memory_count: int
    used_memory_count: int
    total_storage_count: int
    used_storage_count: int


class SubmitTaskRequest(BaseModel):
    task_name: str
    task_image: str
    inst_num: int
    plan_cpu: int
    plan_mem: int
    plan_gpu: int
    runtime: int
    fs_files: list[str]


class TaskLogResponse(BaseModel):
    task_id: str
    logs: dict[int, str]


class RequestSubmitRequest(BaseModel):
    message: str


class BenchmarkRequest(BaseModel):
    num_prompts: int
    qps: float


class BenchmarkProgressResponse(BaseModel):
    total: int
    completed: int


class BenchmarkResultResponse(BaseModel):
    prompt_lens: list[int]
    response_lens: list[int]
    end_to_end_latencies: list[float]
    prefill_latencies: list[float]
