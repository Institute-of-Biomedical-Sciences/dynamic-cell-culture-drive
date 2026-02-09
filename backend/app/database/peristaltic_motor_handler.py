"""Peristaltic Motor Database Operations."""

import json
from typing import Any, Dict, List, Optional

from app.database.database import db
from app.models import (
    PeristalticCalibration,
    PeristalticScenario,
    TubeConfiguration,
)

# ---------------------------------------------------------
# Tube configurations
# ---------------------------------------------------------


def save_tube_configuration(tube_configuration: TubeConfiguration) -> bool:
    """Save a tube configuration."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tube_configurations (name, diameter, flow_rate, preset)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        tube_configuration.name,
                        tube_configuration.diameter,
                        tube_configuration.flow_rate,
                        tube_configuration.preset,
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


def update_tube_configuration(tube_configuration: TubeConfiguration) -> bool:
    """Update a tube configuration."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE tube_configurations SET name = %s, diameter = %s, flow_rate = %s WHERE id = %s
                    """,
                    (
                        tube_configuration.name,
                        tube_configuration.diameter,
                        tube_configuration.flow_rate,
                        tube_configuration.id,
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


def get_tube_configuration(name: str) -> TubeConfiguration:
    """Get a tube configuration by name."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, diameter, flow_rate, preset
                    FROM tube_configurations WHERE name = %s
                """,
                    (name,),
                )
                return TubeConfiguration.model_validate(dict(cur.fetchone()))
    except Exception:
        conn.rollback()
        raise


def get_tube_configurations() -> List[TubeConfiguration]:
    """Get all tube configurations from database."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, diameter, flow_rate, preset
                    FROM tube_configurations
                """
                )
                return [
                    TubeConfiguration.model_validate(dict(row))
                    for row in cur.fetchall()
                ]
    except Exception:
        conn.rollback()
        raise


# ---------------------------------------------------------
# Peristaltic calibration
# ---------------------------------------------------------


def save_peristaltic_calibration(
    duration: int,
    low_rpm: int,
    high_rpm: int,
    low_rpm_volume: float,
    high_rpm_volume: float,
    slope: float,
    name: str,
    diameter: float,
):
    """Save calibration data."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO peristaltic_calibrations (duration, low_rpm, high_rpm, low_rpm_volume, high_rpm_volume, slope, name, diameter)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        duration,
                        low_rpm,
                        high_rpm,
                        low_rpm_volume,
                        high_rpm_volume,
                        slope,
                        name,
                        diameter,
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


def update_peristaltic_calibration(calibration: PeristalticCalibration):
    """Update a peristaltic calibration."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE peristaltic_calibrations SET name= %s, slope = %s, diameter = %s WHERE id = %s
                    """,
                    (
                        calibration.name,
                        calibration.slope,
                        calibration.diameter,
                        calibration.id
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


def get_peristaltic_calibration(name: str) -> PeristalticCalibration:
    """Get a peristaltic calibration by name."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, duration, low_rpm, high_rpm, low_rpm_volume, high_rpm_volume, slope, name, diameter
            FROM peristaltic_calibrations WHERE name = %s
        """,
            (name,),
        )
        return PeristalticCalibration.model_validate(dict(cur.fetchone()))


def get_peristaltic_calibrations() -> List[PeristalticCalibration]:
    """Get all peristaltic calibrations from database."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, duration, low_rpm, high_rpm, low_rpm_volume, high_rpm_volume, slope, name, diameter
            FROM peristaltic_calibrations
        """
        )
        return [
            PeristalticCalibration.model_validate(dict(row)) for row in cur.fetchall()
        ]


# ---------------------------------------------------------
# Peristaltic scenarios
# ---------------------------------------------------------


def get_peristaltic_scenarios() -> List[PeristalticScenario]:
    """Get all peristaltic scenarios from database."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, movements, calibration
            FROM peristaltic_scenarios WHERE is_active = TRUE
            ORDER BY name
        """
        )
        return [PeristalticScenario.model_validate(dict(row)) for row in cur.fetchall()]


def get_peristaltic_scenario(scenario_id: str) -> Optional[PeristalticScenario]:
    """Get a single peristaltic scenario by ID."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, movements, calibration
            FROM peristaltic_scenarios
            WHERE id = %s
        """,
            (scenario_id,),
        )
        result = cur.fetchone()
        return PeristalticScenario.model_validate(dict(result)) if result else None


def save_peristaltic_scenario(scenario: PeristalticScenario) -> int:
    """Save a new peristaltic scenario and return its ID."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO peristaltic_scenarios
                    (name, movements, calibration)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """,
                    (
                        scenario.name,
                        json.dumps([m.model_dump() for m in scenario.movements]),
                        json.dumps(scenario.calibration.model_dump()),
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return result["id"]
    except Exception:
        conn.rollback()
        raise


def update_peristaltic_scenario(
    scenario_id: int, scenario: PeristalticScenario
) -> bool:
    """Update an existing peristaltic scenario."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE peristaltic_scenarios
                    SET name = %s, movements = %s
                    WHERE id = %s
                """,
                    (
                        scenario.name,
                        json.dumps([m.model_dump() for m in scenario.movements]),
                        scenario_id,
                    ),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


def remove_peristaltic_scenario(scenario_id: int) -> bool:
    """Delete a peristaltic scenario."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE peristaltic_scenarios SET is_active = FALSE WHERE id = %s",
                    (scenario_id,),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


# ---------------------------------------------------------
# Entry Operations
# ---------------------------------------------------------


def create_entry(
    name: str,
    peristaltic_scenario_id: Optional[int] = None,
    scenario_name: Optional[str] = None,
) -> int:
    """Create a new entry and return its ID."""
    from datetime import datetime

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO peristaltic_entry_table (name, peristaltic_scenario_id, scenario_name, measurement_timestamp)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (name, peristaltic_scenario_id, scenario_name, datetime.now()),
                )
                result = cur.fetchone()
                conn.commit()
                return int(result["id"])
    except Exception:
        conn.rollback()
        raise


def get_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    """Get an entry by ID."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, peristaltic_scenario_id, scenario_name, measurement_timestamp
            FROM peristaltic_entry_table
            WHERE id = %s
        """,
            (entry_id,),
        )
        result = cur.fetchone()
        return dict(result) if result else None


def get_entries() -> List[Dict[str, Any]]:
    """Get all entries."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, peristaltic_scenario_id, scenario_name, name, measurement_timestamp
            FROM peristaltic_entry_table
            ORDER BY measurement_timestamp DESC
        """
        )
        return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------
# Measurements
# ---------------------------------------------------------


def create_peristaltic_measurement(measurement_data: Dict[str, Any]) -> str:
    """Create a new peristaltic measurement and return its ID."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO peristaltic_measurements
                    (entry_id, speed, direction)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """,
                    (
                        measurement_data["entry_id"],
                        measurement_data["speed"],
                        measurement_data["direction"],
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return str(result["id"])
    except Exception:
        conn.rollback()
        raise


def create_peristaltic_measurements_batch(measurements: List[Dict[str, Any]]) -> int:
    """Create multiple peristaltic measurements in a single batch insert."""
    if not measurements:
        return 0
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Prepare values for batch insert
                # Convert timestamp (float) back to datetime for PostgreSQL
                values = [
                    (
                        m["entry_id"],
                        m["flow"],
                        m["direction"],
                        m["time"],
                    )
                    for m in measurements
                ]

                cur.executemany(
                    """
                    INSERT INTO peristaltic_measurements
                    (entry_id, flow, direction, time)
                    VALUES (%s, %s, %s, %s)
                """,
                    values,
                )
                conn.commit()
                return cur.rowcount
    except Exception:
        conn.rollback()
        raise


def get_measurements(
    entry_id: Optional[str] = None,
    peristaltic_scenario_id: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """Get peristaltic measurements with optional filters."""
    with db.get_cursor() as cur:
        # Use a subquery to get the most recent N measurements, then order them ASC for display
        query = """
            SELECT id, entry_id, flow, direction, time
            FROM (
                SELECT id, entry_id, flow, direction, time
                FROM peristaltic_measurements
                WHERE 1=1
        """
        params = []

        if entry_id:
            query += " AND entry_id = %s"
            params.append(entry_id)

        query += """
                ORDER BY time DESC
                LIMIT %s
            ) AS recent_measurements
            ORDER BY time ASC
        """
        params.append(limit)

        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
