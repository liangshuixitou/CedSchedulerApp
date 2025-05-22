from fastapi import FastAPI
from fastapi import HTTPException

from cedschedulerapp.worker.args import server_config
from cedschedulerapp.worker.schemas import NodeResourceStatsResponse
from cedschedulerapp.worker.service import get_node_stats

app = FastAPI()


@app.get("/node/stats", response_model=NodeResourceStatsResponse)
async def get_node_stats_endpoint():
    try:
        return get_node_stats()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=server_config.host, port=server_config.port, reload=server_config.reload)
