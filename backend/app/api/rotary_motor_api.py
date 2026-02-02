from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.handlers.rotary_motor import rotary_motor_handler
from app.auth import get_current_active_user
from app.models import (
    EntryResponse,
    RotaryMeasurementResponse,
    RotateMotorRequest,
    RotationScenario,
    User,
)

router = APIRouter(prefix="/rotate", tags=["rotate"])


# ============================================================
# Motor control
# ============================================================


@router.post("/rotate")
def rotate_motor(
    request: RotateMotorRequest, current_user: User = Depends(get_current_active_user)
):
    """Rotate motor from min to max in non-stop motion."""
    try:
        success = rotary_motor_handler.rotate_motor(
            entry_name=request.entry_name,
            scenario_id=request.scenario_id,
            scenario_name=request.scenario_name,
            movements=request.movements,
        )
        return {"success": success, "message": "Rotate motor started."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"Error rotating rotary motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stop-rotate")
def stop_rotate(current_user: User = Depends(get_current_active_user)):
    """Stop rotate motor."""
    try:
        success = rotary_motor_handler.stop_rotate_motor()
        return {"success": success, "message": "Rotate motor stopped."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pause-rotate")
def pause_rotate(current_user: User = Depends(get_current_active_user)):
    """Pause rotate motor."""
    try:
        success = rotary_motor_handler.pause_rotate_motor()
        return {"success": success, "message": "Rotate motor paused."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resume-rotate")
def resume_rotate(movement: int, current_user: User = Depends(get_current_active_user)):
    """Resume rotate motor."""
    try:
        success = rotary_motor_handler.resume_rotate_motor(movement)
        return {"success": success, "message": "Rotate motor resumed."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Rotation scenarios
# ============================================================


@router.get("/rotation-scenarios")
def get_rotation_scenarios(current_user: User = Depends(get_current_active_user)):
    """Get list of rotary scenarios."""
    try:
        scenarios = rotary_motor_handler.get_rotation_scenarios()
        return scenarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rotary scenarios api calls


@router.post("/rotation-scenario")
def save_rotation_scenario(
    scenario: RotationScenario,
    current_user: User = Depends(get_current_active_user),
):
    """Save a rotation scenario."""
    try:
        if scenario.name == "":
            raise HTTPException(status_code=400, detail="Scenario name is required")
        scenario_id = rotary_motor_handler.save_rotation_scenario(scenario)
        return {
            "success": True,
            "message": "Rotation scenario saved.",
            "rotation_scenario_id": scenario_id,
        }
    except Exception as e:
        print(f"Error saving rotation scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rotation-scenario/{scenario_id}")
def update_rotation_scenario(
    scenario_id: int,
    scenario: RotationScenario,
    current_user: User = Depends(get_current_active_user),
):
    """Update a rotation scenario."""
    try:
        success = rotary_motor_handler.update_rotation_scenario(scenario_id, scenario)
        return {
            "success": success,
            "message": "Rotation scenario updated.",
        }
    except Exception as e:
        print(f"Error updating rotation scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rotation-scenario/{scenario_id}")
def remove_rotation_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Remove a rotary scenario."""
    try:
        success = rotary_motor_handler.remove_rotation_scenario(scenario_id)
        return {"success": success, "message": "Rotary scenario removed."}
    except Exception as e:
        print(f"Error removing rotary scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Status
# ============================================================


@router.get("/status")
def get_status(current_user: User = Depends(get_current_active_user)):
    """Get current motor status."""
    try:
        status = rotary_motor_handler.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Entries
# ============================================================


@router.get("/entries", response_model=list[EntryResponse])
def get_rotary_entries(
    current_user: User = Depends(get_current_active_user),
):
    """Get all measurement entries."""
    try:
        entries = rotary_motor_handler.get_entries()
        return [
            EntryResponse(
                id=str(entry["id"]),
                scenario_id=entry["rotary_scenario_id"]
                if entry["rotary_scenario_id"]
                else None,
                name=entry["name"],
                scenario_name=entry["scenario_name"]
                if entry["scenario_name"]
                else None,
                type=1,
                measurement_timestamp=entry["measurement_timestamp"].isoformat(),
            )
            for entry in entries
        ]
    except Exception as e:
        print(f"Error getting entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Measurements
# ============================================================


@router.get("/measurements", response_model=list[RotaryMeasurementResponse])
def get_measurements(
    entry_id: str = Query(..., description="Filter by entry ID (required)"),
    limit: int = Query(1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
):
    """Get rotary measurements for a specific entry."""
    try:
        measurements = rotary_motor_handler.get_measurements(
            entry_id=entry_id, limit=limit
        )
        return [
            RotaryMeasurementResponse(
                id=str(m["id"]),
                entry_id=m["entry_id"],
                speed=m["speed"],
                direction=m["direction"],
                time=m["time"],
            )
            for m in measurements
        ]
    except Exception as e:
        print(f"Error retrieving measurements: {e}")
        raise HTTPException(status_code=500, detail=str(e))
