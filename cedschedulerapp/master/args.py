import argparse
from dataclasses import dataclass


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    training_host: str = "127.0.0.1"
    training_port: int = 5000


def parse_args() -> ServerConfig:
    parser = argparse.ArgumentParser(description="CedScheduler Worker Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口号 (默认: 8000)")

    args = parser.parse_args()
    return ServerConfig(host=args.host, port=args.port)


server_config = parse_args()
