from fastapi import FastAPI
from fastapi.responses import JSONResponse

from cedschedulerapp.master.args import server_config
from cedschedulerapp.master.manager import global_manager
from cedschedulerapp.master.schemas import NodeResourceStats
from cedschedulerapp.master.schemas import ResourceStats

app = FastAPI()


@app.post("/node/heartbeat", response_model=NodeResourceStats)
async def receive_heartbeat(stats: NodeResourceStats):
    """接收来自worker节点的心跳信息"""
    try:
        await global_manager.update_node_stats(stats.node_id, stats)
        return stats
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"更新节点状态失败: {str(e)}", "success": False})


@app.get("/resources/stats", response_model=ResourceStats)
async def get_resource_stats():
    try:
        return await global_manager.get_resource_stats()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取资源统计失败: {str(e)}", "success": False})


@app.get("/resources/nodes_stats", response_model=list[NodeResourceStats])
async def get_nodes_stats():
    try:
        return await global_manager.get_all_node_stats()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"获取所有节点状态失败: {str(e)}", "success": False})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=server_config.host, port=server_config.port)
