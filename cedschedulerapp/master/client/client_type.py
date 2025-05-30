from pydantic import BaseModel

from cedschedulerapp.master.enums import TaskInstDataStatus
from cedschedulerapp.master.enums import TaskInstStatus
from cedschedulerapp.master.enums import TaskStatus


class TaskInst(BaseModel):
    task_id: str
    inst_id: int
    inst_status: TaskStatus


class TaskMeta(BaseModel):
    # task metadata
    task_id: str
    task_name: str
    task_inst_num: int
    task_plan_cpu: float
    task_plan_mem: float
    task_plan_gpu: int
    task_status: TaskStatus
    task_start_time: float
    task_runtime: dict[str, int]


class ScheduleInfo(BaseModel):
    # for each inst in task
    inst_id: int
    gpu_id: str


class TaskWrapRuntimeInfo(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    task_meta: TaskMeta
    schedule_infos: dict[int, ScheduleInfo]
    inst_status: dict[int, TaskInstStatus]
    inst_data_status: dict[int, TaskInstDataStatus]
    task_submit_time: float
    task_start_time: float
    task_end_time: float


# TaskMeta 相关模型
class TaskMetaModel(BaseModel):
    task_id: str
    task_name: str
    task_inst_num: int
    task_plan_cpu: float
    task_plan_mem: float
    task_plan_gpu: int
    task_status: TaskStatus
    task_start_time: float
    task_runtime: dict[str, float]

    def to_task_meta(self) -> TaskMeta:
        return TaskMeta(
            task_id=self.task_id,
            task_name=self.task_name,
            task_inst_num=self.task_inst_num,
            task_plan_cpu=self.task_plan_cpu,
            task_plan_mem=self.task_plan_mem,
            task_plan_gpu=self.task_plan_gpu,
            task_status=self.task_status,
            task_start_time=self.task_start_time,
            task_runtime=self.task_runtime,
        )

    @classmethod
    def from_task_meta(cls, task_meta: TaskMeta) -> "TaskMetaModel":
        return cls(
            task_id=task_meta.task_id,
            task_name=task_meta.task_name,
            task_inst_num=task_meta.task_inst_num,
            task_plan_cpu=task_meta.task_plan_cpu,
            task_plan_mem=task_meta.task_plan_mem,
            task_plan_gpu=task_meta.task_plan_gpu,
            task_status=task_meta.task_status,
            task_start_time=task_meta.task_start_time,
            task_runtime=task_meta.task_runtime,
        )


class ManagerTaskSubmitModel(BaseModel):
    task: TaskMetaModel


class InferenceInstanceInfo(BaseModel):
    instance_id: str
    gpu_count: int
    request_count: int
    running_request_count: int
    waiting_request_count: int
    total_gpu_blocks_count: int
    used_gpu_blocks_count: int
    waiting_gpu_blocks_count: int
