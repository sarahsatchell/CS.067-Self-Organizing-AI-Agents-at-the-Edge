import asyncio
import json
import os
from aiohttp import web
import aiohttp
import NodeClass
import OldNodeClass
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
                algorithm = data.get("algorithm", "aco")  # default to ACO if not specified

                await ws.send_str(json.dumps({
                    "type": "ack",
                    "algorithm": algorithm,
                    "status": "Maze received. Starting swarm simulation..."
                }))

                asyncio.create_task(run_live_simulation(maze, start, end, ws, algorithm))

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
async def run_live_simulation(maze, start, end, ws, algorithm: str = "aco"):
    if algorithm == "aco":
        # Trigger optimised ACO algorithm (NodeClass.Node)
        agents = spawn_agents(maze, tuple(start), node_class=NodeClass.Node)
    else:
        # Trigger original frontier-based algorithm (OldNodeClass.OldNode)
        agents = spawn_agents(maze, tuple(start), node_class=OldNodeClass.OldNode)

    listener_tasks = [asyncio.create_task(agent.web_listen()) for agent in agents]

    for agent in agents:
        await ws.send_str(json.dumps({
            "type": "agent_registered",
            "algorithm": algorithm,
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "position": list(agent.aco_current_position) if algorithm == "aco" else list(agent.current_position),
            "status": "exploring"
        }))

    tick = 0
    goal_reached = False

    # Helper: normalise position attribute across both agent types
    def get_position(agent):
        if algorithm == "aco":
            return agent.aco_current_position
        return agent.current_position

    while not goal_reached and tick < 500:
        tick += 1
        agent_data = []

        for agent in agents:
            agent.tick(maze)
            pos = get_position(agent)

            if pos == tuple(end):
                goal_reached = True
                reached_attr = "aco_reached_goal" if algorithm == "aco" else "reached_goal"
                goal_tick_attr = "aco_goal_tick" if algorithm == "aco" else "goal_tick"

                if not getattr(agent, reached_attr):
                    setattr(agent, reached_attr, True)
                    setattr(agent, goal_tick_attr, tick)

                await ws.send_str(json.dumps({
                    "type": "agent_goal_reached",
                    "algorithm": algorithm,
                    "agent_name": agent.name,
                    "agent_id": agent.agent_id,
                    "position": list(pos),
                    "tick": tick
                }))

            # Normalise map/frontier attributes across both agent types
            if algorithm == "aco":
                local_map = agent.aco_local_map
                target_frontier = agent.aco_target_frontier
            else:
                local_map = agent.local_map
                target_frontier = agent.target_frontier

            agent_data.append({
                "id": agent.agent_id,
                "position": pos,
                "target_frontier": target_frontier,
                "cells_discovered": len(local_map)
            })

        explored = set()
        for agent in agents:
            map_attr = "aco_local_map" if algorithm == "aco" else "local_map"
            explored.update(getattr(agent, map_attr).keys())

        total_open = sum(1 for row in maze for cell in row if cell == 0)
        explored_pct = (len(explored) / total_open * 100) if total_open > 0 else 0

        await ws.send_str(json.dumps({
            "type": "tick_update",
            "algorithm": algorithm,
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
        map_attr = "aco_local_map" if algorithm == "aco" else "local_map"
        explored.update(getattr(agent, map_attr).keys())

    total_open = sum(1 for row in maze for cell in row if cell == 0)
    explored_pct = (len(explored) / total_open * 100) if total_open > 0 else 0

    agent_stats = []
    for agent in agents:
        stats = agent.get_agent_stats(tuple(end), maze, explored)
        agent_stats.append(stats)

    await ws.send_str(json.dumps({
        "type": "simulation_complete",
        "algorithm": algorithm,
        "goal_reached": goal_reached,
        "tick": tick,
        "explored_cells": len(explored),
        "total_cells": total_open,
        "explored_pct": round(explored_pct, 1),
        "agent_stats": agent_stats
    }))


# -------------------------
# HTTP health check
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
    app.router.add_route("*", "/ws", websocket_handler)

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