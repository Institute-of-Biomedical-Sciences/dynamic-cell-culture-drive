import asyncio
import json
from typing import Any, Dict, Set

from fastapi import WebSocket

from app.asyncio_loop import get_event_loop


class WebSocketManager:
    """Manages WebSocket connections and broadcasts motor updates."""

    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    # ---------------------------------------------------------
    # Event loop binding (MANDATORY)
    # ---------------------------------------------------------

    def _submit(self, coro):
        try:
            loop = get_event_loop()
            asyncio.run_coroutine_threadsafe(coro, loop)
        except Exception as e:
            print(f"Async submission error: {e}")

    # ---------------------------------------------------------
    # Connection handling
    # ---------------------------------------------------------

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""

        async def _disconnect():
            async with self._lock:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
            print(
                f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
            )

        # Schedule disconnect in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_disconnect())
            else:
                asyncio.run(_disconnect())
        except RuntimeError:
            # No event loop, try to get/create one
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_disconnect())
                loop.close()
            except Exception as e:
                print(f"Error disconnecting WebSocket: {e}")

    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = set()

        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
                    disconnected.add(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections.discard(connection)

    async def send_repetitions(self, repetitions: int):
        """Send repetitions to all connected clients."""
        await self.broadcast(
            {
                "type": "repetitions",
                "data": {
                    "repetitions": repetitions,
                },
            }
        )

    async def send_measurements(self, measurements: list[Dict[str, Any]]):
        """Send measurements to all connected clients."""
        for measurement in measurements:
            await self.broadcast(
                {
                    "type": "tilt",
                    "data": {
                        "angle": measurement["angle"],
                        "state": measurement["state"],
                        "time": measurement["time"],
                    },
                }
            )

    async def send_rotate_measurements(self, measurements: list[Dict[str, Any]]):
        """Send a rotate measurement update to all connected clients."""
        for measurement in measurements:
            await self.broadcast(
                {
                    "type": "rotate",
                    "data": {
                        "speed": measurement["speed"],
                        "direction": measurement["direction"],
                        "time": measurement["time"],
                    },
                }
            )

    async def send_peristaltic_measurements(self, measurements: list[Dict[str, Any]]):
        """Send peristaltic measurements to all connected clients."""
        for measurement in measurements:
            await self.broadcast(
                {
                    "type": "peristaltic",
                    "data": {
                        "speed": measurement["speed"],
                        "direction": measurement["direction"],
                        "time": measurement["time"],
                    },
                }
            )

    async def send_rotate_movement(self, movement: int):
        """Send a rotate movement update to all connected clients."""
        await self.broadcast(
            {
                "type": "rotate_movement",
                "data": {
                    "movement": movement,
                },
            }
        )

    async def send_motor_update(self, position: float, status: str, is_moving: bool):
        """Send a motor status update to all connected clients."""
        await self.broadcast(
            {
                "type": "motor_update",
                "data": {
                    "position": position,
                    "status": status,
                    "is_moving": is_moving,
                },
            }
        )

    async def send_tilt_stopped(self):
        """Send a measurement update to all connected clients."""
        await self.broadcast(
            {
                "type": "tilt",
                "data": {
                    "tilt_stopped": True,
                },
            }
        )

    async def send_rotate_stopped(self):
        """Send a measurement update to all connected clients."""
        await self.broadcast(
            {
                "type": "rotate",
                "data": {
                    "rotate_stopped": True,
                },
            }
        )

    async def send_peristaltic_stopped(self):
        """Send a peristaltic stopped update to all connected clients."""
        await self.broadcast(
            {
                "type": "peristaltic",
                "data": {
                    "peristaltic_stopped": True,
                },
            }
        )

    async def send_peristaltic_movement(self, movement: int):
        """Send a peristaltic movement update to all connected clients."""
        await self.broadcast(
            {
                "type": "peristaltic_movement",
                "data": {
                    "movement": movement,
                },
            }
        )


# Global WebSocket manager instance
manager = WebSocketManager()
