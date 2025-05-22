from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel

from cedschedulerapp.master.enums import NodeType
from cedschedulerapp.master.enums import RegionType

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 0
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


class TrainingTask(BaseModel):
    id: str
    name: str
    start_time: str
    region: RegionType


class InferenceService(BaseModel):
    id: str
    name: str
    start_time: str
    region: RegionType


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
