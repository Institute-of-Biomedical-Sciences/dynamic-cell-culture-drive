from enum import Enum
from typing import Optional

from pydantic import BaseModel

# =========================
# Common / Shared Models
# =========================


class MotorStatus(str, Enum):
    """Status of the motor."""

    IDLE = "idle"
    MOVING = "moving"
    ERROR = "error"


class User(BaseModel):
    """User model."""

    username: str
    disabled: bool


class Configuration(BaseModel):
    """Configuration model."""

    fullscale_current: float
    idle_current: float
    isgain: int
    microstepping: int
    overheat_current: float
    torque: float


# =========================
# Tilt Motor
# =========================


class TiltMotorRequest(BaseModel):
    """Request model for tilt motor."""

    entry_name: str
    scenario_name: str | None
    scenario_id: int | None
    min_tilt: int
    max_tilt: int
    move_duration: float
    repetitions: int
    end_position: int
    microstepping: int
    standstill_duration_left: Optional[float]
    standstill_duration_horizontal: Optional[float]
    standstill_duration_right: Optional[float]


class MoveScenario(BaseModel):
    """Move scenario model (tilt)."""

    id: Optional[int]
    name: str
    microstepping: int
    min_tilt: int
    max_tilt: int
    repetitions: int
    move_duration: float
    end_position: int
    standstill_duration_left: float
    standstill_duration_horizontal: float
    standstill_duration_right: float


class EntryCreate(BaseModel):
    """Entry creation model for tilt."""

    name: str
    tilt_scenario_id: int
    scenario_name: str


class EntryResponse(BaseModel):
    """Tilt entry response model."""

    id: int
    scenario_id: Optional[int]
    scenario_name: Optional[str]
    name: str
    measurement_timestamp: str
    type: int


class TiltMeasurementCreate(BaseModel):
    """Tilt measurement creation model."""

    entry_id: int
    tilt_scenario_id: int
    angle: float
    state: MotorStatus


class TiltMeasurementResponse(BaseModel):
    """Tilt measurement response model."""

    id: int
    entry_id: int
    angle: float
    state: str
    time: float


# =========================
# Rotary Motor
# =========================


class Movement(BaseModel):
    """Movement model for rotary motor."""

    duration: int
    direction: str
    rpm: float


class RotateMotorRequest(BaseModel):
    """Request model for rotate motor."""

    entry_name: str
    scenario_id: int | None = None
    scenario_name: str | None = None
    movements: list[Movement]


class RotationScenario(BaseModel):
    """Rotation scenario model."""

    id: Optional[int]
    name: str
    movements: list[Movement]


class RotaryEntryResponse(BaseModel):
    """Rotary entry response model."""

    id: int
    rotary_scenario_id: Optional[int]
    scenario_name: Optional[str]
    name: str
    measurement_timestamp: str


class RotaryMeasurementCreate(BaseModel):
    """Rotary measurement creation model."""

    entry_id: int
    rotary_scenario_id: int
    speed: float
    direction: str


class RotaryMeasurementResponse(BaseModel):
    """Rotary measurement response model."""

    id: int
    entry_id: int
    speed: float
    direction: str
    time: float


# =========================
# Peristaltic Motor
# =========================


class PeristalticMovement(BaseModel):
    """Peristaltic movement model for peristaltic motor."""

    duration: int
    flow: float
    direction: str


class PeristalticRotateRequest(BaseModel):
    """Request model for peristaltic motor movement."""

    entry_name: str
    scenario_id: int | None = None
    scenario_name: str | None = None
    calibration_name: str
    calibration_preset: bool
    movements: list[PeristalticMovement]


class PeristalticEntryResponse(BaseModel):
    """Peristaltic entry response model."""

    id: int
    peristaltic_scenario_id: Optional[int]
    name: str
    scenario_name: Optional[str]
    measurement_timestamp: str


class PeristalticMeasurement(BaseModel):
    """Peristaltic measurement model."""

    id: int
    entry_id: int
    flow: float
    direction: str
    time: float


class TubeConfiguration(BaseModel):
    """Tube configuration model."""

    id: Optional[int]
    name: str
    diameter: float
    flow_rate: float
    preset: bool


class PeristalticCalibration(BaseModel):
    """Peristaltic calibration model (stored in DB)."""

    id: Optional[int]
    duration: int
    low_rpm: float
    high_rpm: float
    low_rpm_volume: float
    high_rpm_volume: float
    slope: float
    name: str


class PeristalticSlopeCompute(BaseModel):
    """Peristaltic slope compute model."""

    duration: int
    low_rpm: float
    high_rpm: float
    low_rpm_volume: float
    high_rpm_volume: float


class PeristalticScenario(BaseModel):
    """Peristaltic scenario model."""

    id: Optional[int]
    name: str
    movements: list[PeristalticMovement]
    calibration: PeristalticCalibration | TubeConfiguration


class PeristalticMotorCalibrationRequest(BaseModel):
    """Request model for peristaltic motor calibration."""

    duration: int
    low_rpm: float
    high_rpm: float
    low_rpm_volume: float
    high_rpm_volume: float
    name: str


class RPMCalibrationRequest(BaseModel):
    """Request model for generic RPM calibration."""

    duration: int
    rpm: float
    direction: str

class PeristalticMeasurementResponse(BaseModel):
    """Peristaltic measurement response model."""

    id: int
    entry_id: int
    flow: float
    direction: str
    time: float