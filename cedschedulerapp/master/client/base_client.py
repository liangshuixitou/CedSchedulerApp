from typing import Optional

import requests

from cedschedulerapp.utils.logger import setup_logger


class ClientBase:
    def __init__(self, ip: str, port: int):
        self.base_url = f"http://{ip}:{port}"
        self.logger = setup_logger(__name__)

    async def _make_request(self, endpoint: str, data: dict) -> Optional[dict]:
        """
        发送HTTP请求到服务器

        Args:
            endpoint: API端点路径
            data: 请求数据

        Returns:
            Optional[dict]: 响应数据，失败时返回None
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # 如果HTTP请求返回了不成功的状态码，将抛出HTTPError异常
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to {url} failed: {e}")
            return None

    async def get_request(self, endpoint: str) -> Optional[dict]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to {url} failed: {e}")
            return None
