import argparse
from dataclasses import dataclass

from cedschedulerapp.worker.enums import NodeType
from cedschedulerapp.worker.enums import RegionType


@dataclass
class ServerConfig:
    master_host: str = "127.0.0.1"
    master_port: int = 8000
    reload: bool = False
    node_id: str = "cedscheduler-worker"
    region: str = "Cloud"
    node_type: str = "Training"


def parse_args() -> ServerConfig:
    parser = argparse.ArgumentParser(description="CedScheduler Worker Server")
    parser.add_argument("--master-host", type=str, default="127.0.0.1", help="Master主机地址 (默认: 127.0.0.1)")
    parser.add_argument("--master-port", type=int, default=8000, help="Master端口号 (默认: 8000)")
    parser.add_argument("--reload", action="store_true", help="是否启用热重载 (默认: False)")
    parser.add_argument("--id", type=str, required=True, help="节点ID")
    parser.add_argument(
        "--region",
        type=str,
        required=True,
        choices=[e.value for e in RegionType],
        help=f"节点区域，可选: {[e.value for e in RegionType]}",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=[e.value for e in NodeType],
        help=f"节点类型，可选: {[e.value for e in NodeType]}",
    )

    args = parser.parse_args()
    return ServerConfig(
        master_host=args.master_host,
        master_port=args.master_port,
        reload=args.reload,
        node_id=args.id,
        region=args.region,
        node_type=args.type,
    )


server_config = parse_args()
