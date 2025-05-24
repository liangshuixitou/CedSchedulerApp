from cedschedulerapp.master.client.base_client import ClientBase
from cedschedulerapp.master.client.client_type import ManagerTaskSubmitModel
from cedschedulerapp.master.client.client_type import TaskMeta
from cedschedulerapp.master.client.client_type import TaskMetaModel
from cedschedulerapp.utils.logger import setup_logger


class TraingingServerClient(ClientBase):
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)
        self.logger = setup_logger(__name__)

    async def list_tasks(self):
        response = await self._make_request("/api/task/infos", {})
        if response is None:
            return None
        return list(response.values())

    async def submit_task(self, task_meta: TaskMeta):
        data = ManagerTaskSubmitModel(
            task=TaskMetaModel.from_task_meta(task_meta)
        ).model_dump()
        return await self._make_request("/api/task/submit", data)

    async def get_training_task_log(self, task_id: str) -> dict[int, str]:
        response = await self._make_request(f"/api/task/log/{task_id}", {})
        return response
