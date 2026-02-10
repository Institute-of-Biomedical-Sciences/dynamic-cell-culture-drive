import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from .api.api import router as api_router
from .api.handlers.peristaltic_motor import peristaltic_motor_handler
from .api.handlers.rotary_motor import rotary_motor_handler
from .api.handlers.tilt_motor import tilt_motor_handler
from .api.peristaltic_motor_api import router as peristaltic_router
from .api.rotary_motor_api import router as rotary_router
from .api.tilt_motor_api import router as tilt_router
from .asyncio_loop import set_event_loop
from .auth import (
    authenticate_user,
    create_access_token,
    fake_users_db,
    get_current_active_user,
)
from .config import settings
from .database.database import db
from .models import User
from .websocket_manager import WebSocket, manager


def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("Starting Dynamic Cell Culture Drive Control Software...")

    # DB first (usually quick and should fail fast)
    try:
        db.connect()
        print("Database connection established")
    except Exception as e:
        print(f"Database connection failed: {e}")
    set_event_loop(asyncio.get_running_loop())
    # Functions to run in parallel
    init_tasks = [
        ("Tilt", tilt_motor_handler.initialize),
        ("Rotary", rotary_motor_handler.initialize),
        ("Peristaltic", peristaltic_motor_handler.initialize),
    ]

    with ThreadPoolExecutor(max_workers=len(init_tasks)) as executor:
        futures = {executor.submit(fn): name for name, fn in init_tasks}
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
                print(f"{name} motor initialized successfully")
            except Exception as e:
                print(f"{name} motor initialization failed: {e}")

    print("Motors initialization completed")

    # ---- app runs here ----
    yield

    # Shutdown (can also be parallelized similarly if needed)
    print("Shutting down Dynamic Cell Culture Drive Control Software...")
    try:
        tilt_motor_handler.cleanup()
    except Exception as e:
        print(f"Error cleaning up tilt motor: {e}")
    try:
        rotary_motor_handler.cleanup()
    except Exception as e:
        print(f"Error cleaning up rotary motor: {e}")
    try:
        peristaltic_motor_handler.cleanup()
    except Exception as e:
        print(f"Error cleaning up peristaltic motor: {e}")
    try:
        db.close()
        print("Database connection closed")
    except Exception as e:
        print(f"Error closing database connection: {e}")
    print("Shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Hardware control server for Dynamic Cell Culture Drive system",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tilt_router)
app.include_router(rotary_router)
app.include_router(peristaltic_router)
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Dynamic Cell Culture Drive Control Software",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    from datetime import datetime

    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": datetime.now().isoformat() + "Z",
    }


# Additional authentication endpoint for convenience
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint (alternative to /auth/token)."""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(weeks=settings.access_token_expire_weeks)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/profile")
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@app.websocket("/ws/motor")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time motor updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Error handlers
@app.exception_handler(404)
def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "detail": "The requested resource was not found",
        },
    )


@app.exception_handler(500)
def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
