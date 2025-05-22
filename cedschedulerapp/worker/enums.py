from enum import Enum


class RegionType(str, Enum):
    Cloud = "1"
    Edge = "2"
    Device = "3"


class NodeType(str, Enum):
    Training = "训练"
    Inference = "推理"
