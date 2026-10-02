"""
Synthetic Data Generator
Predictive Maintenance for Industrial Electric Motors

Generates synthetic operating data for an electric motor integrated
into a conveyor system.

IMPORTANT:
The generated data are simulated observations intended for research,
software development, and machine-learning experimentation.
They are not a substitute for measurements from a real industrial motor.
"""

from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42


def generate_motor_data(
    n_samples: int = 10_000,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate synthetic electric-motor operating data.

    Parameters
    ----------
    n_samples : int
        Number of observations to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        Synthetic motor operating dataset.
    """

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # 1. TIME
    # ---------------------------------------------------------

    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=n_samples,
        freq="min",
    )

    operating_hours = np.arange(n_samples) / 60.0

    # ---------------------------------------------------------
    # 2. MOTOR LOAD
    # ---------------------------------------------------------

    load_pct = rng.normal(
        loc=65,
        scale=15,
        size=n_samples,
    )

    load_pct = np.clip(load_pct, 10, 100)

    # ---------------------------------------------------------
    # 3. VOLTAGE
    # ---------------------------------------------------------

    voltage_v = rng.normal(
        loc=230,
        scale=3,
        size=n_samples,
    )

    # ---------------------------------------------------------
    # 4. CURRENT
    #
    # Current increases as motor load increases.
    # ---------------------------------------------------------

    current_a = (
        2.5
        + (load_pct * 0.075)
        + rng.normal(0, 0.35, n_samples)
    )

    # ---------------------------------------------------------
    # 5. TEMPERATURE
    #
    # Temperature is influenced by load and current.
    # ---------------------------------------------------------

    temperature_c = (
        32
        + (load_pct * 0.28)
        + (current_a * 0.8)
        + rng.normal(0, 2.0, n_samples)
    )

    # ---------------------------------------------------------
    # 6. RPM
    #
    # Nominal motor speed with small load-related variation.
    # ---------------------------------------------------------

    rpm = (
        1780
        - (load_pct * 0.35)
        + rng.normal(0, 8, n_samples)
    )

    # ---------------------------------------------------------
    # 7. VIBRATION
    #
    # Mechanical vibration increases slightly with load.
    # ---------------------------------------------------------

    vibration_rms_mm_s = (
        1.0
        + (load_pct * 0.012)
        + rng.normal(0, 0.18, n_samples)
    )

    vibration_rms_mm_s = np.clip(
        vibration_rms_mm_s,
        0.2,
        None,
    )

    # ---------------------------------------------------------
    # 8. APPROXIMATE ELECTRICAL POWER
    #
    # Simplified research variable.
    # ---------------------------------------------------------

    power_kw = (
        voltage_v
        * current_a
        * 0.85
        / 1000
    )

    # ---------------------------------------------------------
    # 9. INITIAL HEALTH INDEX
    # ---------------------------------------------------------

    health_index = np.full(
        n_samples,
        100.0,
    )

    condition = np.full(
        n_samples,
        "NORMAL",
        dtype=object,
    )

    failure_mode = np.full(
        n_samples,
        "NONE",
        dtype=object,
    )

    # ---------------------------------------------------------
    # 10. PROGRESSIVE DEGRADATION
    #
    # Later observations simulate gradual deterioration.
    # ---------------------------------------------------------

    degradation_start = int(n_samples * 0.60)

    degradation = np.zeros(n_samples)

    degradation[degradation_start:] = np.linspace(
        0,
        1,
        n_samples - degradation_start,
    )

    temperature_c += degradation * 15
    vibration_rms_mm_s += degradation * 3.0
    current_a += degradation * 1.8
    rpm -= degradation * 45

    health_index -= degradation * 65

    # ---------------------------------------------------------
    # 11. OPERATING CONDITION
    # ---------------------------------------------------------

    degradation_mask = health_index < 85
    warning_mask = health_index < 60
    failure_mask = health_index < 35

    condition[degradation_mask] = "DEGRADATION"
    condition[warning_mask] = "WARNING"
    condition[failure_mask] = "FAILURE"

    # ---------------------------------------------------------
    # 12. FAILURE MODES
    # ---------------------------------------------------------

    overheating = temperature_c >= 75

    excessive_vibration = vibration_rms_mm_s >= 4.5

    overload = (
        (load_pct >= 90)
        & (current_a >= 9)
    )

    electrical_anomaly = (
        (voltage_v < 220)
        | (voltage_v > 240)
    )

    bearing_degradation = (
        (vibration_rms_mm_s >= 3.5)
        & (temperature_c >= 65)
    )

    failure_mode[overheating] = "OVERHEATING"

    failure_mode[excessive_vibration] = (
        "EXCESSIVE_VIBRATION"
    )

    failure_mode[overload] = "OVERLOAD"

    failure_mode[electrical_anomaly] = (
        "ELECTRICAL_ANOMALY"
    )

    failure_mode[bearing_degradation] = (
        "BEARING_DEGRADATION"
    )

    # ---------------------------------------------------------
    # 13. CREATE DATAFRAME
    # ---------------------------------------------------------

    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "motor_id": "MOTOR_001",
            "temperature_c": temperature_c,
            "vibration_rms_mm_s": vibration_rms_mm_s,
            "current_a": current_a,
            "voltage_v": voltage_v,
            "rpm": rpm,
            "power_kw": power_kw,
            "load_pct": load_pct,
            "operating_hours": operating_hours,
            "health_index": health_index,
            "condition": condition,
            "failure_mode": failure_mode,
        }
    )

    # ---------------------------------------------------------
    # 14. ROUND NUMERIC VARIABLES
    # ---------------------------------------------------------

    numeric_columns = [
        "temperature_c",
        "vibration_rms_mm_s",
        "current_a",
        "voltage_v",
        "rpm",
        "power_kw",
        "load_pct",
        "operating_hours",
        "health_index",
    ]

    data[numeric_columns] = data[numeric_columns].round(2)

    return data


def save_dataset(
    data: pd.DataFrame,
    output_path: str = "data/synthetic/motor_synthetic_data.csv",
) -> None:
    """
    Save the generated synthetic dataset as a CSV file.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        path,
        index=False,
    )

    print(f"Dataset saved to: {path}")
    print(f"Rows: {len(data):,}")


if __name__ == "__main__":

    dataset = generate_motor_data()

    save_dataset(dataset)

    print("\nDataset preview:")
    print(dataset.head())

    print("\nCondition distribution:")
    print(dataset["condition"].value_counts())

    print("\nFailure mode distribution:")
    print(dataset["failure_mode"].value_counts())
