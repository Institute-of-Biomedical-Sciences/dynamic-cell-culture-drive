"""Rotary Motor Database Operations."""

import json
from typing import Any, Dict, List, Optional

from app.database.database import db
from app.models import RotationScenario

# ---------------------------------------------------------
# Rotation scenarios
# ---------------------------------------------------------


def get_rotary_scenarios() -> List[RotationScenario]:
    """Get all rotary scenarios from database."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, movements
            FROM rotary_scenarios WHERE is_active = TRUE
            ORDER BY name
        """
        )
        return [RotationScenario.model_validate(dict(row)) for row in cur.fetchall()]


def get_rotary_scenario(scenario_id: str) -> Optional[RotationScenario]:
    """Get a single rotary scenario by ID."""
    with db.get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, movements
            FROM rotary_scenarios
            WHERE id = %s
        """,
            (scenario_id,),
        )
        result = cur.fetchone()
        return RotationScenario.model_validate(dict(result)) if result else None


def create_rotary_scenario(scenario: RotationScenario) -> int:
    """Create a new rotary scenario and return its ID."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rotary_scenarios
                    (name, movements)
                    VALUES (%s, %s)
                    RETURNING id
                """,
                    (
                        scenario.name,
                        json.dumps([m.model_dump() for m in scenario.movements]),
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return result["id"]
    except Exception:
        conn.rollback()
        raise


def update_rotary_scenario(scenario_id: str, scenario: RotationScenario) -> bool:
    """Update an existing tilt scenario."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE rotary_scenarios
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


def delete_rotary_scenario(scenario_id: str) -> bool:
    """Delete a rotary scenario."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE rotary_scenarios SET is_active = FALSE WHERE id = %s
                """,
                    (scenario_id,),
                )
                conn.commit()
                return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise


# ---------------------------------------------------------
# Entry operations
# ---------------------------------------------------------


def create_entry(
    name: str,
    rotary_scenario_id: Optional[int] = None,
    scenario_name: Optional[str] = None,
) -> int:
    """Create a new entry and return its ID."""
    from datetime import datetime

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rotation_entry_table (name, rotary_scenario_id, scenario_name, measurement_timestamp)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (name, rotary_scenario_id, scenario_name, datetime.now()),
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
            SELECT id, name, rotary_scenario_id, scenario_name, measurement_timestamp
            FROM rotation_entry_table
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
            SELECT id, name, rotary_scenario_id, scenario_name, measurement_timestamp
            FROM rotation_entry_table
            ORDER BY measurement_timestamp DESC
        """
        )
        return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------
# Measurements
# ---------------------------------------------------------


def create_rotary_measurement(measurement_data: Dict[str, Any]) -> str:
    """Create a new rotary measurement and return its ID."""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rotary_measurements
                    (entry_id, speed, direction, time)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        measurement_data["entry_id"],
                        measurement_data["speed"],
                        measurement_data["direction"],
                        measurement_data["time"],
                    ),
                )
                result = cur.fetchone()
                conn.commit()
                return str(result["id"])
    except Exception:
        conn.rollback()
        raise


def create_rotary_measurements_batch(measurements: List[Dict[str, Any]]) -> int:
    """Create multiple rotary measurements in a single batch insert."""
    if not measurements:
        return 0
    try:
        print(measurements)
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Prepare values for batch insert
                # Convert timestamp (float) back to datetime for PostgreSQL
                values = [
                    (
                        m["entry_id"],
                        m["speed"],
                        m["direction"],
                        m["time"],
                    )
                    for m in measurements
                ]

                cur.executemany(
                    """
                    INSERT INTO rotary_measurements
                    (entry_id, speed, direction, time)
                    VALUES (%s, %s, %s, %s)
                """,
                    values,
                )
                conn.commit()
                return cur.rowcount
    except Exception:
        conn.rollback()
        raise


def get_rotary_measurements(
    entry_id: Optional[str] = None,
    rotary_scenario_id: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """Get rotary measurements with optional filters."""
    with db.get_cursor() as cur:
        # Use a subquery to get the most recent N measurements, then order them ASC for display
        query = """
            SELECT id, entry_id, speed, direction, time
            FROM (
                SELECT id, entry_id, speed, direction, time
                FROM rotary_measurements
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
