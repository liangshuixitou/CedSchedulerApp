import asyncio
import os
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List

import httpx
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

app = FastAPI()

class RegionType(str, Enum):
    All = '0'
    Cloud = '1'
    Edge = '2'
    Device = '3'

class NodeType(str, Enum):
    Training = '训练'
    Inference = '推理'

class GPUInfo(BaseModel):
    gpu_id: str
    gpu_type: str
    gpu_memory_total: int
    gpu_memory_used: int
    gpu_utilization: float

class NodeResourceStatsResponse(BaseModel):
    node_id: str
    node_ip: str
    region: RegionType
    node_type: NodeType
    cpu_count: int
    gpu_count: int
    memory_count: int
    storage_count: int
    used_cpu_count: int
    used_gpu_count: int
    used_memory_count: int
    used_storage_count: int
    gpu_info: List[GPUInfo]

class TrainingTask(BaseModel):
    id: str
    name: str
    start_time: str
    region: RegionType

class InferenceService(BaseModel):
    id: str
    name: str
    start_time: str
    region: RegionType

class ResourceStatsResponse(BaseModel):
    cloud_node_count: int
    edge_node_count: int
    device_node_count: int
    total_cpu_count: int
    used_cpu_count: int
    total_gpu_count: int
    used_gpu_count: int
    total_memory_count: int
    used_memory_count: int
    total_storage_count: int
    used_storage_count: int
    training_task_count: int
    inference_service_count: int
    training_tasks: List[TrainingTask]
    inference_services: List[InferenceService]

# Configuration for worker nodes
WORKER_NODES = {
    RegionType.Cloud: ["http://cloud-worker-1:8000", "http://cloud-worker-2:8000"],
    RegionType.Edge: ["http://edge-worker-1:8000", "http://edge-worker-2:8000"],
    RegionType.Device: ["http://device-worker-1:8000"]
}

async def fetch_node_stats(client: httpx.AsyncClient, url: str) -> NodeResourceStatsResponse:
    try:
        response = await client.get(f"{url}/node/stats")
        response.raise_for_status()
        return NodeResourceStatsResponse(**response.json())
    except Exception as e:
        print(f"Error fetching stats from {url}: {e}")
        return None

@app.get("/resource/stats", response_model=ResourceStatsResponse)
async def get_resource_stats():
    async with httpx.AsyncClient() as client:
        # Fetch stats from all workers
        tasks = []
        for region, urls in WORKER_NODES.items():
            for url in urls:
                tasks.append(fetch_node_stats(client, url))
        
        node_stats = await asyncio.gather(*tasks)
        node_stats = [stat for stat in node_stats if stat is not None]

        # Initialize counters
        cloud_node_count = 0
        edge_node_count = 0
        device_node_count = 0
        total_cpu_count = 0
        used_cpu_count = 0
        total_gpu_count = 0
        used_gpu_count = 0
        total_memory_count = 0
        used_memory_count = 0
        total_storage_count = 0
        used_storage_count = 0

        # Aggregate stats
        for stat in node_stats:
            if stat.region == RegionType.Cloud:
                cloud_node_count += 1
            elif stat.region == RegionType.Edge:
                edge_node_count += 1
            elif stat.region == RegionType.Device:
                device_node_count += 1

            total_cpu_count += stat.cpu_count
            used_cpu_count += stat.used_cpu_count
            total_gpu_count += stat.gpu_count
            used_gpu_count += stat.used_gpu_count
            total_memory_count += stat.memory_count
            used_memory_count += stat.used_memory_count
            total_storage_count += stat.storage_count
            used_storage_count += stat.used_storage_count

        # Mock training tasks and inference services for now
        # In a real implementation, these would come from a database or other service
        training_tasks = [
            TrainingTask(
                id="task1",
                name="Training Task 1",
                start_time=datetime.now().isoformat(),
                region=RegionType.Cloud
            )
        ]

        inference_services = [
            InferenceService(
                id="service1",
                name="Inference Service 1",
                start_time=datetime.now().isoformat(),
                region=RegionType.Edge
            )
        ]

        return ResourceStatsResponse(
            cloud_node_count=cloud_node_count,
            edge_node_count=edge_node_count,
            device_node_count=device_node_count,
            total_cpu_count=total_cpu_count,
            used_cpu_count=used_cpu_count,
            total_gpu_count=total_gpu_count,
            used_gpu_count=used_gpu_count,
            total_memory_count=total_memory_count,
            used_memory_count=used_memory_count,
            total_storage_count=total_storage_count,
            used_storage_count=used_storage_count,
            training_task_count=len(training_tasks),
            inference_service_count=len(inference_services),
            training_tasks=training_tasks,
            inference_services=inference_services
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 