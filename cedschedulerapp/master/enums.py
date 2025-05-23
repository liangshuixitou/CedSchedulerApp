from enum import Enum


class RegionType(int, Enum):
    ALL = 0
    Cloud = 1
    Edge = 2
    Device = 3


class NodeType(str, Enum):
    Training = "训练"
    Inference = "推理"


class GPUType(str, Enum):
    V100 = "V100"
    P100 = "P100"
    T4 = "T4"


class GPUPerformance(float, Enum):
    T4_PERFORMANCE = 8.1
    P100_PERFORMANCE = 9.3
    V100_PERFORMANCE = 15.7


class TaskStatus(str, Enum):
    Submitted = "submitted"
    Pending = "pending"
    Ready = "ready"
    Running = "running"
    Finished = "finished"


class TaskInstStatus(str, Enum):
    Pending = "pending"
    Ready = "ready"
    Running = "running"
    Finished = "finished"


class TaskInstDataStatus(str, Enum):
    Pending = "pending"
    Running = "running"
    Finished = "finished"
