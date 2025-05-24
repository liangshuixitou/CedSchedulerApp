from cedschedulerapp.master.client.base_client import ClientBase
from cedschedulerapp.master.client.client_type import InferenceInstanceInfo
from cedschedulerapp.utils.logger import setup_logger


class InferenceServerClient(ClientBase):
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)
        self.logger = setup_logger(__name__)

    async def list_instances(self) -> list[InferenceInstanceInfo]:
        """获取推理实例列表"""
        response = await self.get_request("/instance_list")
        if response is None:
            return []

        response = response.get("data", [])
        instances = []
        for instance_data in response:
            instance = InferenceInstanceInfo(
                instance_id=instance_data["instance_id"],
                gpu_count=instance_data["gpu_count"],
                request_count=instance_data["request_count"],
                running_request_count=instance_data["running_request_count"],
                waiting_request_count=instance_data["waiting_request_count"],
                total_gpu_blocks_count=instance_data["total_gpu_blocks_count"],
                used_gpu_blocks_count=instance_data["used_gpu_blocks_count"],
                waiting_gpu_blocks_count=instance_data["waiting_gpu_blocks_count"],
            )
            instances.append(instance)
        return instances

    async def get_instance_log(self, instance_id: str) -> str:
        response = await self.get_request(f"/instance_log/{instance_id}")
        if response is None:
            return ""
        response = response.get("data", "")
        return response

    async def generate(self, prompt: str) -> str:
        sampling_params = {"temperature": 0.7, "top_p": 0.9, "max_tokens": 512}
        request_body = {"prompt": prompt, "stream": False, **sampling_params}
        response = await self._make_request("/generate", request_body)

        if response is None:
            return ""
        return response

    async def benchmark(self, num_prompts: int, qps: float) -> str:
        response = await self._make_request(
            "/benchmark", {"num_prompts": num_prompts, "qps": qps}
        )
        if response is None:
            return ""

        response = response.get("data", "")
        self.logger.info(response)
        return response.get("benchmark_id", "")

    async def benchmark_result(self, benchmark_id: str) -> str:
        response = await self.get_request(f"/benchmark_result/{benchmark_id}")
        if response is None:
            return ""

        response = response.get("data", "")
        self.logger.info(response)
        return response
