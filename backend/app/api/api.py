from fastapi import APIRouter, Depends, HTTPException

from app.api.handlers.peristaltic_motor import peristaltic_motor_handler
from app.api.handlers.rotary_motor import rotary_motor_handler
from app.api.handlers.tilt_motor import tilt_motor_handler
from app.auth import get_current_active_user
from app.models import User

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def get_general_status(current_user: User = Depends(get_current_active_user)):
    """Get general status of all motors."""
    try:
        # Get individual motor statuses
        tilt_status = tilt_motor_handler.get_status()
        rotary_status = rotary_motor_handler.get_status()
        peristaltic_status = peristaltic_motor_handler.get_status()

        # Determine movement types
        tilt_movement_type = None
        if tilt_status.get("is_moving", False):
            # Check if tilt motor is running
            if (
                hasattr(tilt_motor_handler, "_tilt_motor_running")
                and tilt_motor_handler._tilt_motor_running
            ):
                tilt_movement_type = "tilt"

        rotary_movement_type = None
        if rotary_status.get("is_moving", False):
            # Check if rotate motor is running
            if (
                hasattr(rotary_motor_handler, "_rotate_motor_running")
                and rotary_motor_handler._rotate_motor_running
            ):
                rotary_movement_type = "rotate"

        peristaltic_movement_type = None
        if peristaltic_status.get("is_moving", False):
            # Check if peristaltic rotate motor is running
            if (
                hasattr(peristaltic_motor_handler, "_rotate_motor_running")
                and peristaltic_motor_handler._rotate_motor_running
            ):
                peristaltic_movement_type = "rotate"

        return {
            "tilt": {
                "status": tilt_status.get("status"),
                "is_moving": tilt_status.get("is_moving", False),
                "movement_type": tilt_movement_type,
                "position": tilt_status.get("position"),
                "initialized": tilt_status.get("initialized", False),
            },
            "rotary": {
                "status": rotary_status.get("status"),
                "is_moving": rotary_status.get("is_moving", False),
                "movement_type": rotary_movement_type,
                "position": rotary_status.get("position"),
                "initialized": rotary_status.get("initialized", False),
            },
            "peristaltic": {
                "status": peristaltic_status.get("status"),
                "is_moving": peristaltic_status.get("is_moving", False),
                "movement_type": peristaltic_movement_type,
                "position": peristaltic_status.get("position"),
                "initialized": peristaltic_status.get("initialized", False),
            },
        }
    except Exception as e:
        print(f"Error getting general status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
