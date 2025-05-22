import re
import socket
import subprocess

from cedschedulerapp.worker.schemas import GPUInfo


def get_nvidia_gpu_info() -> list[GPUInfo]:
    try:
        import GPUtil

        gpus = GPUtil.getGPUs()
        if not gpus:
            print("No NVIDIA GPUs found on this system")
            return []
        return [
            GPUInfo(
                gpu_id=str(gpu.id),
                gpu_type=gpu.name,
                gpu_memory_total=int(gpu.memoryTotal),
                gpu_memory_used=int(gpu.memoryUsed),
                gpu_utilization=float(gpu.load * 100),
            )
            for gpu in gpus
        ]
    except ImportError as err:
        print("GPUtil is not installed. Please install it using: pip install gputil")
        raise ImportError("GPUtil is not installed") from err
    except Exception as err:
        print(f"Error getting NVIDIA GPU info: {err}")
        raise RuntimeError("Failed to get NVIDIA GPU information") from err


def get_tianshu_gpu_info() -> list[GPUInfo]:
    try:
        result = subprocess.run(["ixsmi"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running ixsmi:", result.stderr.strip())
            return []

        output = result.stdout
        lines = output.splitlines()

        gpus = []
        current_gpu = None

        for line in lines:
            # 匹配 GPU 开始行，如 "| 0    Iluvatar BI-V100"
            match = re.match(r"^\|\s+(\d+)\s+(\S+\s+\S+)\s+\|", line)
            if match:
                if current_gpu:
                    gpus.append(current_gpu)
                current_gpu = {
                    "gpu_id": match.group(1),
                    "gpu_type": match.group(2).strip(),
                    "gpu_memory_total": 0,
                    "gpu_memory_used": 0,
                    "gpu_utilization": 0,
                }
                print(f"Found GPU: {current_gpu}")  # 调试信息

            # 匹配显存使用情况，如 "| 0%   28C   P0    59W / 250W   | 257MiB / 32768MiB    | 0%        Default    |"
            mem_match = re.search(
                r"\|\s+\d+%\s+\d+C\s+\w+\s+\d+W\s+/\s+\d+W\s+\|\s+(\d+)MiB\s+/\s+(\d+)MiB\s+\|\s+(\d+)%", line
            )
            if mem_match and current_gpu is not None:
                try:
                    used = int(mem_match.group(1))
                    total = int(mem_match.group(2))
                    utilization = int(mem_match.group(3))
                    current_gpu["gpu_memory_used"] = used
                    current_gpu["gpu_memory_total"] = total
                    current_gpu["gpu_utilization"] = utilization
                    print(f"Updated GPU info: {current_gpu}")  # 调试信息
                except Exception as e:
                    print(f"Error parsing GPU info: {e}")  # 调试信息

        if current_gpu:
            gpus.append(current_gpu)

        print(f"Final GPU list: {gpus}")  # 调试信息

        # 确保所有必需的字段都存在
        result = [
            GPUInfo(
                gpu_id=gpu["gpu_id"],
                gpu_type=gpu["gpu_type"],
                gpu_memory_total=gpu["gpu_memory_total"],
                gpu_memory_used=gpu["gpu_memory_used"],
                gpu_utilization=gpu["gpu_utilization"],
            )
            for gpu in gpus
        ]
        print(f"Created GPUInfo objects: {result}")  # 调试信息
        return result

    except Exception as err:
        print(f"Error getting 天数 GPU info: {err}")
        import traceback

        traceback.print_exc()  # 打印完整的错误堆栈
        return []


def get_gpu_info() -> list[GPUInfo]:
    """
    自动检测是否支持 NVIDIA GPU，优先使用 NVIDIA 方式；
    否则尝试使用天数智芯 ixsmi 获取 GPU 信息。
    """
    try:
        # 尝试导入 GPUtil 并获取 GPU 信息
        import GPUtil

        gpus = GPUtil.getGPUs()
        if gpus:
            print("Detected NVIDIA GPU, using GPUtil...")
            return get_nvidia_gpu_info()
    except (ImportError, Exception):
        pass

    print("No NVIDIA GPU detected, trying 天数智芯 ixsmi...")
    return get_tianshu_gpu_info()


def get_node_ip() -> str:
    try:
        # 创建一个临时socket连接来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接一个外部地址（不需要真实连接）
        s.connect(("8.8.8.8", 80))
        # 获取本地IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as err:
        raise RuntimeError("Failed to get node IP address") from err
