"""
generate_synthetic_patients.py
===============================
Produces synthetic longitudinal lab records for 4 personas used by TrendSight.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.

All patient data is synthetic/generated. Never use or reference real patient data.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List
import os

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

rng = np.random.default_rng(seed=42)  # fixed seed for reproducibility


def _add_noise(values: np.ndarray, noise_std: float) -> np.ndarray:
    """Add small gaussian noise to a value array."""
    return values + rng.normal(0, noise_std, size=values.shape)


def _linear_trend(
    start: float,
    end: float,
    n_visits: int,
    noise_std: float = 0.0,
) -> np.ndarray:
    """Create a linearly trending series plus optional noise."""
    trend = np.linspace(start, end, n_visits)
    if noise_std > 0:
        trend = _add_noise(trend, noise_std)
    return np.maximum(trend, 0.0)  # no negative lab values


def _flat_with_spike(
    baseline: float,
    spike_value: float,
    spike_index: int,
    n_visits: int,
    noise_std: float = 0.0,
) -> np.ndarray:
    """Flat values except for a single spike at a given visit index."""
    vals = np.full(n_visits, baseline)
    vals[spike_index] = spike_value
    if noise_std > 0:
        vals = _add_noise(vals, noise_std)
    return np.maximum(vals, 0.0)


# ---------------------------------------------------------------------------
# Persona definition
# ---------------------------------------------------------------------------

@dataclass
class LabMarker:
    name: str
    unit: str
    normal_low: float
    normal_high: float
    values: List[float] = field(default_factory=list)


@dataclass
class Persona:
    name: str
    age: int
    tags: List[str]
    markers: List[LabMarker] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def make_maria(n_visits: int = 12) -> Persona:
    """
    Maria, 54. eGFR declining 68→52, creatinine 0.9→1.4 over 18 months.
    Tag: rural, limited transport, 2 PCP visits/year.
    """
    # ~1.5 months between visits → every 6 weeks
    dates = pd.date_range("2024-01-15", periods=n_visits, freq="6W")

    egfr = _linear_trend(68, 52, n_visits, noise_std=1.8)
    creat = _linear_trend(0.9, 1.4, n_visits, noise_std=0.04)

    p = Persona(
        name="Maria",
        age=54,
        tags=["rural", "limited transport", "2 PCP visits/year"],
        markers=[
            LabMarker(
                name="eGFR",
                unit="mL/min/1.73m²",
                normal_low=60,
                normal_high=120,
                values=egfr.tolist(),
            ),
            LabMarker(
                name="Creatinine",
                unit="mg/dL",
                normal_low=0.6,
                normal_high=1.2,
                values=creat.tolist(),
            ),
        ],
    )
    # Attach dates
    p.dates = dates  # type: ignore[attr-defined]
    return p


def make_james(n_visits: int = 12) -> Persona:
    """
    James, 39. HbA1c rising 5.6→6.6 over 24 months, small steps, small noise.
    Tag: insured, urban, easy pharmacy access.
    """
    # ~2 months between visits (spans ~24 months)
    dates = pd.date_range("2024-01-15", periods=n_visits, freq="2MS")

    hba1c = _linear_trend(5.6, 6.6, n_visits, noise_std=0.08)

    p = Persona(
        name="James",
        age=39,
        tags=["insured", "urban", "easy pharmacy access"],
        markers=[
            LabMarker(
                name="HbA1c",
                unit="%",
                normal_low=4.0,
                normal_high=5.7,
                values=hba1c.tolist(),
            ),
        ],
    )
    p.dates = dates  # type: ignore[attr-defined]
    return p


def make_aisha(n_visits: int = 12) -> Persona:
    """
    Aisha, 28. All labs fluctuate normally within range, no real trend.
    3-4 common markers: Hb, WBC, sodium, calcium.
    """
    dates = pd.date_range("2024-01-15", periods=n_visits, freq="6W")

    # Normal reference ranges from general clinical knowledge
    # Hemoglobin (g/dL): normal ~12-16 for women (commonly)
    # WBC (K/µL): normal ~4.5-11.0
    # Sodium (mmol/L): normal ~135-145
    # Calcium (mg/dL): normal ~8.5-10.5
    n = n_visits
    hb = _add_noise(np.full(n, 13.8), 0.6)
    wbc = _add_noise(np.full(n, 7.0), 0.9)
    sodium = _add_noise(np.full(n, 140), 1.5)
    calcium = _add_noise(np.full(n, 9.5), 0.3)

    p = Persona(
        name="Aisha",
        age=28,
        tags=["urban", "no known barriers"],
        markers=[
            LabMarker(
                name="Hemoglobin", unit="g/dL", normal_low=12.0, normal_high=16.0,
                values=hb.tolist(),
            ),
            LabMarker(
                name="WBC", unit="K/µL", normal_low=4.5, normal_high=11.0,
                values=wbc.tolist(),
            ),
            LabMarker(
                name="Sodium", unit="mmol/L", normal_low=135, normal_high=145,
                values=sodium.tolist(),
            ),
            LabMarker(
                name="Calcium", unit="mg/dL", normal_low=8.5, normal_high=10.5,
                values=calcium.tolist(),
            ),
        ],
    )
    p.dates = dates  # type: ignore[attr-defined]
    return p


def make_robert(n_visits: int = 15) -> Persona:
    """
    Robert, 61. Flat history except one acute potassium spike at one visit.
    """
    dates = pd.date_range("2024-01-15", periods=n_visits, freq="6W")

    # Potassium normal: 3.5 - 5.0 mEq/L
    k = _flat_with_spike(
        baseline=4.2, spike_value=5.8, spike_index=7,
        n_visits=n_visits, noise_std=0.15,
    )
    # Also give him eGFR and creatinine for variety (flat + normal)
    egfr = _add_noise(np.full(n_visits, 75), 2.0)
    creat = _add_noise(np.full(n_visits, 1.0), 0.05)

    p = Persona(
        name="Robert",
        age=61,
        tags=["urban", "monitored for hypertension"],
        markers=[
            LabMarker(
                name="Potassium", unit="mEq/L", normal_low=3.5, normal_high=5.0,
                values=k.tolist(),
            ),
            LabMarker(
                name="eGFR", unit="mL/min/1.73m²", normal_low=60, normal_high=120,
                values=egfr.tolist(),
            ),
            LabMarker(
                name="Creatinine", unit="mg/dL", normal_low=0.6, normal_high=1.2,
                values=creat.tolist(),
            ),
        ],
    )
    p.dates = dates  # type: ignore[attr-defined]
    return p


# ---------------------------------------------------------------------------
# DataFrame export
# ---------------------------------------------------------------------------

def persona_to_dataframe(p: Persona) -> pd.DataFrame:
    """
    Convert a Persona into a long-format DataFrame:
      visit_date, name, age, tags, marker, value, unit, normal_low, normal_high
    """
    rows = []
    for m in p.markers:
        for i, v in enumerate(m.values):
            rows.append(
                {
                    "visit_date": p.dates[i],  # type: ignore[attr-defined]
                    "name": p.name,
                    "age": p.age,
                    "tags": "; ".join(p.tags),
                    "marker": m.name,
                    "value": round(v, 2),
                    "unit": m.unit,
                    "normal_low": m.normal_low,
                    "normal_high": m.normal_high,
                }
            )
    return pd.DataFrame(rows)


def generate_all_personas() -> dict:
    """Return a dict of {persona_name: Persona} for all 4 personas."""
    return {
        "Maria": make_maria(),
        "James": make_james(),
        "Aisha": make_aisha(),
        "Robert": make_robert(),
    }


def generate_all_dataframes() -> dict:
    """Return a dict of {persona_name: DataFrame} for all 4 personas."""
    return {k: persona_to_dataframe(v) for k, v in generate_all_personas().items()}


# ---------------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dfs = generate_all_dataframes()
    for name, df in dfs.items():
        print(f"\n{'='*50}")
        print(f"  {name}")
        print(f"{'='*50}")
        print(df.to_string(index=False))
    print("\n✅ Synthetic data generated successfully.")
