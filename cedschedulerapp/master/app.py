from fastapi import FastAPI

from cedschedulerapp.master.args import server_config
from cedschedulerapp.master.manager import global_manager
from cedschedulerapp.master.schemas import APIResponse
from cedschedulerapp.master.schemas import NodeResourceStats
from cedschedulerapp.master.schemas import ResourceStats

app = FastAPI()


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


@app.get("/resources/nodes_stats", response_model=APIResponse[list[NodeResourceStats]])
async def get_nodes_stats():
    try:
        stats = await global_manager.get_all_node_stats()
        return APIResponse(data=stats)
    except Exception as e:
        return APIResponse(code=500, message=f"获取所有节点状态失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=server_config.host, port=server_config.port)
