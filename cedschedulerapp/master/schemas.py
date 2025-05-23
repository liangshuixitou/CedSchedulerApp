from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel

from cedschedulerapp.master.client.types import ScheduleInfo, TaskWrapRuntimeInfo
from cedschedulerapp.master.enums import NodeType, TaskInstStatus, TaskStatus
from cedschedulerapp.master.enums import RegionType

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
    start_time: str

    @classmethod
    def from_training_task_detail(cls, task: TrainingTaskDetail):
        return cls(
            id=task.task_id,
            name=task.task_name,
            start_time=task.task_start_time,
        )


class InferenceService(BaseModel):
    id: str
    name: str
    start_time: str


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
    training_task_count: int
    inference_service_count: int
    training_tasks: list[TrainingTask]
    inference_services: list[InferenceService]


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
