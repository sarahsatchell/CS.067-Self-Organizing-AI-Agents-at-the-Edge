import asyncio
import json
import os
from aiohttp import web
import aiohttp
import NodeClass
from spawner import spawn_agents

connected_clients = set()
event_loop = None


# -------------------------
# WebSocket handler (Frontend → Python)
# -------------------------
async def websocket_handler(request):
    ws = web.WebSocketResponse(protocols=["chat"])
    await ws.prepare(request)

    connected_clients.add(ws)
    print("New client connected")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                maze = data.get("maze")
                start = data.get("start")
                end = data.get("end")

                await ws.send_str(json.dumps({
                    "type": "ack",
                    "status": "Maze received. Starting swarm simulation..."
                }))

                asyncio.create_task(run_live_simulation(maze, start, end, ws))

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")

    except Exception as e:
        print(f"WebSocket handler error: {e}")
    finally:
        connected_clients.discard(ws)
        print("Client disconnected")

    return ws


# -------------------------
# UDP Node listener (Node → Python)
# -------------------------
node = NodeClass.Node(9000, "Node1", 0)


def on_udp_message(msg, addr):
    print(f"Node received message: {msg} from {addr}")
    asyncio.run_coroutine_threadsafe(broadcast(msg), event_loop)


node.on_message = on_udp_message


# -------------------------
# Broadcast to all connected WebSocket clients
# -------------------------
async def broadcast(message):
    if not connected_clients:
        return

    try:
        payload = json.loads(message)
    except Exception:
        payload = {"type": "node_message", "payload": message}

    msg_str = json.dumps(payload)
    await asyncio.gather(
        *(ws.send_str(msg_str) for ws in connected_clients),
        return_exceptions=True
    )


# -------------------------
# Simulation logic
# -------------------------
async def run_live_simulation(maze, start, end, ws):
    agents = spawn_agents(maze, tuple(start))

    listener_tasks = [asyncio.create_task(agent.web_listen()) for agent in agents]

    for agent in agents:
        await ws.send_str(json.dumps({
            "type": "agent_registered",
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "position": list(agent.current_position),
            "status": "exploring"
        }))

    tick = 0
    goal_reached = False

    while not goal_reached and tick < 500:
        tick += 1
        agent_data = []

        for agent in agents:
            agent.tick(maze)

            if agent.current_position == tuple(end):
                goal_reached = True
                if not agent.reached_goal:
                    agent.reached_goal = True
                    agent.goal_tick = tick
                await ws.send_str(json.dumps({
                    "type": "agent_goal_reached",
                    "agent_name": agent.name,
                    "agent_id": agent.agent_id,
                    "position": list(agent.current_position),
                    "tick": tick
                }))

            agent_data.append({
                "id": agent.agent_id,
                "position": agent.current_position,
                "target_frontier": agent.target_frontier,
                "cells_discovered": len(agent.local_map)
            })

        explored = set()
        for agent in agents:
            explored.update(agent.local_map.keys())
        total_open = sum(1 for row in maze for cell in row if cell == 0)
        explored_pct = (len(explored) / total_open * 100) if total_open > 0 else 0

        await ws.send_str(json.dumps({
            "type": "tick_update",
            "tick": tick,
            "goal_reached": goal_reached,
            "explored_pct": round(explored_pct, 1),
            "discovered_cell_positions": [list(cell) for cell in explored],
            "agents": agent_data
        }))

        await asyncio.sleep(0.1)

    # Final summary
    explored = set()
    for agent in agents:
        explored.update(agent.local_map.keys())

    total_open = sum(1 for row in maze for cell in row if cell == 0)
    explored_pct = (len(explored) / total_open * 100) if total_open > 0 else 0

    agent_stats = []
    for agent in agents:
        stats = agent.get_agent_stats(tuple(end), maze, explored)
        agent_stats.append(stats)

    await ws.send_str(json.dumps({
        "type": "simulation_complete",
        "goal_reached": goal_reached,
        "tick": tick,
        "explored_cells": len(explored),
        "total_cells": total_open,
        "explored_pct": round(explored_pct, 1),
        "agent_stats": agent_stats
    }))


# -------------------------
# HTTP health check (HEAD is handled automatically by aiohttp for GET routes)
# -------------------------
async def health_check(request):
    return web.Response(text="OK", status=200)


# -------------------------
# Main entry point
# -------------------------
async def main():
    global event_loop
    event_loop = asyncio.get_running_loop()

    port = int(os.environ.get("PORT", "10000"))

    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/ws", websocket_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    udp_listener = asyncio.create_task(node.web_listen())

    print(f"🚀 Server running on port {port}")
    print(f"   Health check → GET /")
    print(f"   WebSocket    → GET /ws")

    try:
        await asyncio.gather(
            asyncio.Event().wait(),
            udp_listener
        )
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())