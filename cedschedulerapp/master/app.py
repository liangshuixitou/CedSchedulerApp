from fastapi import FastAPI

from cedschedulerapp.master.args import server_config
from cedschedulerapp.master.enums import RegionType
from cedschedulerapp.master.manager import global_manager
from cedschedulerapp.master.schemas import APIResponse
from cedschedulerapp.master.schemas import NodeResourceStats
from cedschedulerapp.master.schemas import ResourceStats
from cedschedulerapp.master.schemas import SubmitTaskRequest
from cedschedulerapp.master.schemas import TaskLogResponse
from cedschedulerapp.master.schemas import TrainingTask
from cedschedulerapp.utils.logger import setup_logger

app = FastAPI()
logger = setup_logger(__name__)


@app.post("/node/heartbeat", response_model=APIResponse[NodeResourceStats])
async def receive_heartbeat(stats: NodeResourceStats):
    """接收来自worker节点的心跳信息"""
    try:
        await global_manager.update_node_stats(stats.node_id, stats)
        return APIResponse(data=stats)
    except Exception as e:
        return APIResponse(code=500, message=f"更新节点状态失败: {str(e)}")


@app.get("/resources/stats", response_model=APIResponse[ResourceStats])
async def get_resource_stats():
    try:
        stats = await global_manager.get_resource_stats()
        return APIResponse(data=stats)
    except Exception as e:
        return APIResponse(code=500, message=f"获取资源统计失败: {str(e)}")


@app.get("/resources/node_stats", response_model=APIResponse[list[NodeResourceStats]])
async def get_nodes_stats(region: RegionType):
    try:
        if region == RegionType.ALL:
            stats = await global_manager.get_all_node_stats()
        else:
            stats = await global_manager.get_nodes_stats_by_region(region)
        return APIResponse(data=stats)
    except Exception as e:
        return APIResponse(code=500, message=f"获取所有节点状态失败: {str(e)}")


@app.get("/training/task_list", response_model=APIResponse[list[TrainingTask]])
async def get_training_task_list():
    try:
        stats = await global_manager.get_training_task_list()
        return APIResponse(data=stats)
    except Exception as e:
        return APIResponse(code=500, message=f"获取训练任务列表失败: {str(e)}")


@app.post("/training/task_submit", response_model=APIResponse[int])
async def submit_task(request: list[SubmitTaskRequest]):
    """提交任务到调度系统"""
    try:
        await global_manager.submit_task(request)
        logger.info(request)
        return APIResponse()
    except Exception as e:
        return APIResponse(code=500, message=f"任务提交失败: {str(e)}")


@app.post("/training/task_log/{task_id}", response_model=APIResponse[TaskLogResponse])
async def update_task(task_id: str):
    """更新训练任务状态"""
    try:
        task_log = await global_manager.get_training_task_log(task_id)
        return APIResponse(data=task_log)
    except Exception as e:
        return APIResponse(code=500, message=f"任务更新失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=server_config.host, port=server_config.port)
