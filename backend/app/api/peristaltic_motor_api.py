from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.handlers.peristaltic_motor import peristaltic_motor_handler
from app.auth import get_current_active_user
from app.models import (
    EntryResponse,
    PeristalticCalibration,
    PeristalticMotorCalibrationRequest,
    PeristalticRotateRequest,
    PeristalticScenario,
    PeristalticSlopeCompute,
    RotaryMeasurementResponse,
    RPMCalibrationRequest,
    TubeConfiguration,
    User,
)

router = APIRouter(prefix="/peristaltic", tags=["peristaltic"])


# ============================================================
# Calibration & Tube Configuration
# ============================================================


@router.post("/calibrate-rotate")
def calibrate_rotate_motor(
    request: RPMCalibrationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Calibrate peristaltic motor RPM."""
    try:
        success = peristaltic_motor_handler.start_rpm_calibration(
            duration=request.duration,
            rpm=request.rpm,
        )
        return {"success": success, "message": "Peristaltic motor calibrated."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"Error calibrating peristaltic motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stop-calibrate")
def stop_calibrate(current_user: User = Depends(get_current_active_user)):
    """Stop RPM calibration."""
    try:
        success = peristaltic_motor_handler.stop_rpm_calibration()
        return {"success": success, "message": "Peristaltic motor calibration stopped."}
    except Exception as e:
        print(f"Error stopping peristaltic motor calibration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calibration/compute-slope")
def compute_slope(
    request: PeristalticSlopeCompute,
    current_user: User = Depends(get_current_active_user),
):
    """Compute calibration slope (flow rate per RPM) without saving."""
    try:
        print(
            f"Computing slope for duration: {request.duration}, low_rpm: {request.low_rpm}, high_rpm: {request.high_rpm}, low_rpm_volume: {request.low_rpm_volume}, high_rpm_volume: {request.high_rpm_volume}"
        )
        slope = peristaltic_motor_handler._compute_slope(
            duration=request.duration,
            low_rpm=request.low_rpm,
            high_rpm=request.high_rpm,
            low_rpm_volume=request.low_rpm_volume,
            high_rpm_volume=request.high_rpm_volume,
        )
        return {"slope": slope}
    except Exception as e:
        print(f"Error computing slope: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calibrate")
def calibrate_motor(
    request: PeristalticMotorCalibrationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Save a peristaltic motor calibration."""
    try:
        slope = peristaltic_motor_handler.save_calibration(
            duration=request.duration,
            low_rpm=request.low_rpm,
            high_rpm=request.high_rpm,
            low_rpm_volume=request.low_rpm_volume,
            high_rpm_volume=request.high_rpm_volume,
            name=request.name,
        )
        return {
            "success": True,
            "slope": slope,
            "message": "Peristaltic motor calibration saved.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"Error saving peristaltic motor calibration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/calibration")
def update_peristaltic_calibration(
    calibration: PeristalticCalibration,
    current_user: User = Depends(get_current_active_user),
):
    """Update a peristaltic calibration."""
    try:
        success = peristaltic_motor_handler.update_peristaltic_calibration(calibration)
        return {"success": success, "message": "Peristaltic calibration updated."}
    except Exception as e:
        print(f"Error updating peristaltic calibration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calibrations")
def get_peristaltic_calibrations(
    current_user: User = Depends(get_current_active_user),
):
    """Get all peristaltic calibrations."""
    try:
        return peristaltic_motor_handler.get_peristaltic_calibrations()
    except Exception as e:
        print(f"Error getting peristaltic calibrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tube-configurations")
def get_tube_configurations(current_user: User = Depends(get_current_active_user)):
    """Get all tube configurations."""
    try:
        tube_configurations = peristaltic_motor_handler.get_tube_configurations()
        return {"tube_configurations": tube_configurations}
    except Exception as e:
        print(f"Error getting tube configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tube-configuration")
def update_tube_configuration(
    tube_configuration: TubeConfiguration,
    current_user: User = Depends(get_current_active_user),
):
    """Update a tube configuration."""
    try:
        success = peristaltic_motor_handler.update_tube_configuration(
            tube_configuration
        )
        return {"success": success, "message": "Tube configuration updated."}
    except Exception as e:
        print(f"Error updating tube configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tube-configuration")
def save_tube_configuration(
    tube_configuration: TubeConfiguration,
    current_user: User = Depends(get_current_active_user),
):
    """Save a tube configuration."""
    try:
        success = peristaltic_motor_handler.save_tube_configuration(tube_configuration)
        return {"success": success, "message": "Tube configuration saved."}
    except Exception as e:
        print(f"Error saving tube configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Peristaltic Motor Control (Rotate)
# ============================================================


@router.post("/rotate")
def rotate_motor(
    request: PeristalticRotateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Start peristaltic rotation based on a scenario + calibration."""
    try:
        success = peristaltic_motor_handler.rotate_motor(
            entry_name=request.entry_name,
            scenario_id=request.scenario_id,
            scenario_name=request.scenario_name,
            calibration_name=request.calibration_name,
            calibration_preset=request.calibration_preset,
            movements=request.movements,
        )
        return {"success": success, "message": "Rotate motor started."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"Error rotating peristaltic motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stop-rotate")
def stop_rotate(current_user: User = Depends(get_current_active_user)):
    """Stop peristaltic motor rotation."""
    try:
        success = peristaltic_motor_handler.stop_peristaltic_motor()
        return {"success": success, "message": "Rotate motor stopped."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pause-rotate")
def pause_rotate(current_user: User = Depends(get_current_active_user)):
    """Pause peristaltic motor rotation."""
    try:
        success = peristaltic_motor_handler.pause_peristaltic_motor()
        return {"success": success, "message": "Peristaltic motor paused."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resume-rotate")
def resume_rotate(movement: int, current_user: User = Depends(get_current_active_user)):
    """Resume peristaltic motor rotation."""
    try:
        success = peristaltic_motor_handler.resume_peristaltic_motor(movement)
        return {"success": success, "message": "Peristaltic motor resumed."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Peristaltic Scenarios
# ============================================================


@router.get("/peristaltic-scenarios")
def get_peristaltic_scenarios(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of peristaltic scenarios."""
    try:
        scenarios = peristaltic_motor_handler.get_peristaltic_scenarios()
        return scenarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/peristaltic-scenario")
def save_peristaltic_scenario(
    scenario: PeristalticScenario,
    current_user: User = Depends(get_current_active_user),
):
    """Save a peristaltic scenario."""
    try:
        if scenario.name == "":
            raise HTTPException(status_code=400, detail="Scenario name is required")
        scenario_id = peristaltic_motor_handler.save_peristaltic_scenario(scenario)
        return {
            "success": True,
            "message": "Peristaltic scenario saved.",
            "peristaltic_scenario_id": scenario_id,
        }
    except Exception as e:
        print(f"Error saving peristaltic scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/peristaltic-scenario/{scenario_id}")
def update_peristaltic_scenario(
    scenario_id: int,
    scenario: PeristalticScenario,
    current_user: User = Depends(get_current_active_user),
):
    """Update a peristaltic scenario."""
    try:
        success = peristaltic_motor_handler.update_peristaltic_scenario(
            scenario_id, scenario
        )
        return {
            "success": success,
            "message": "Peristaltic scenario updated.",
        }
    except Exception as e:
        print(f"Error updating peristaltic scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/peristaltic-scenario/{scenario_id}")
def remove_peristaltic_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Remove a peristaltic scenario."""
    try:
        success = peristaltic_motor_handler.remove_peristaltic_scenario(scenario_id)
        return {"success": success, "message": "Peristaltic scenario removed."}
    except Exception as e:
        print(f"Error removing peristaltic scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Status
# ============================================================


@router.get("/status")
def get_status(current_user: User = Depends(get_current_active_user)):
    """Get current peristaltic motor status."""
    try:
        status = peristaltic_motor_handler.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Entries & Measurements (DB-related)
# ============================================================


@router.get("/entries", response_model=list[EntryResponse])
def get_peristaltic_entries(
    current_user: User = Depends(get_current_active_user),
):
    """Get all measurement entries."""
    try:
        entries = peristaltic_motor_handler.get_entries()
        return [
            EntryResponse(
                id=str(entry["id"]),
                scenario_id=entry["peristaltic_scenario_id"]
                if entry["peristaltic_scenario_id"]
                else None,
                name=entry["name"],
                scenario_name=entry["scenario_name"]
                if entry["scenario_name"]
                else None,
                type=2,
                measurement_timestamp=entry["measurement_timestamp"].isoformat(),
            )
            for entry in entries
        ]

    except Exception as e:
        print(f"Error getting entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/measurements", response_model=list[RotaryMeasurementResponse])
def get_measurements(
    entry_id: str = Query(..., description="Filter by entry ID (required)"),
    limit: int = Query(1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
):
    """Get peristaltic measurements for a specific entry."""
    try:
        measurements = peristaltic_motor_handler.get_measurements(
            entry_id=entry_id, limit=limit
        )
        return [
            RotaryMeasurementResponse(
                id=m["id"],
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
