from fastapi import FastAPI, HTTPException
from .types import NodeResourceStatsResponse
from .service import get_node_stats

app = FastAPI()

@app.get("/node/stats", response_model=NodeResourceStatsResponse)
async def get_node_stats_endpoint():
    try:
        return get_node_stats()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
