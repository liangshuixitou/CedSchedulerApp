from enum import Enum
from typing import List
from pydantic import BaseModel

class RegionType(str, Enum):
    All = '0'
    Cloud = '1'
    Edge = '2'
    Device = '3'

class NodeType(str, Enum):
    Training = '训练'
    Inference = '推理'

class GPUInfo(BaseModel):
    gpu_id: str
    gpu_type: str
    gpu_memory_total: int
    gpu_memory_used: int
    gpu_utilization: float

class NodeResourceStatsResponse(BaseModel):
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
    gpu_info: List[GPUInfo] 