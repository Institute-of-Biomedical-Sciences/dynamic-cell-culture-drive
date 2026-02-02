"""Single asyncio event loop for the application (main thread)."""

import asyncio

asyncio_loop: asyncio.AbstractEventLoop | None = None


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Set the main asyncio event loop."""
    global asyncio_loop
    asyncio_loop = loop


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Get the main asyncio event loop."""
    if asyncio_loop is None:
        raise RuntimeError("Asyncio event loop not initialized")
    return asyncio_loop
