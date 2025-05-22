import asyncio
from datetime import datetime

import httpx

from cedschedulerapp.worker.args import server_config
from cedschedulerapp.worker.schemas import NodeResourceStats
from cedschedulerapp.worker.service import get_node_stats

HEARTBEAT_INTERVAL = 5


async def send_heartbeat():
    """定期向master发送心跳"""
    while True:
        try:
            # 获取当前节点状态
            stats: NodeResourceStats = get_node_stats()

            # 发送心跳到master
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{server_config.master_host}:{server_config.master_port}/node/heartbeat",
                    json=stats.model_dump(),
                )
                response.raise_for_status()
                print(f"Heartbeat sent successfully at {datetime.now()}")

        except Exception as e:
            print(f"Error sending heartbeat: {e}")

        # 等待HEARTBEAT_INTERVAL秒后发送下一次心跳
        await asyncio.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    # 创建事件循环
    loop = asyncio.get_event_loop()
    try:
        # 运行心跳任务
        loop.run_until_complete(send_heartbeat())
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        loop.close()
