import argparse
from dataclasses import dataclass


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    training_host: str = "127.0.0.1"
    training_port: int = 5000
    inference_host: str = "127.0.0.1"
    inference_port: int = 5001

def parse_args() -> ServerConfig:
    parser = argparse.ArgumentParser(description="CedScheduler Worker Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口号 (默认: 8000)")
    parser.add_argument("--training-host", type=str, default="127.0.0.1", help="训练服务器主机地址 (默认: 127.0.0.1)")
    parser.add_argument("--training-port", type=int, default=5000, help="训练服务器端口号 (默认: 5000)")
    parser.add_argument("--inference-host", type=str, default="127.0.0.1", help="推理服务器主机地址 (默认: 127.0.0.1)")
    parser.add_argument("--inference-port", type=int, default=5001, help="推理服务器端口号 (默认: 5001)")

    args = parser.parse_args()
    return ServerConfig(
        host=args.host,
        port=args.port,
        training_host=args.training_host,
        training_port=args.training_port,
        inference_host=args.inference_host,
        inference_port=args.inference_port,
    )


server_config = parse_args()
