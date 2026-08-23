# TrendSight — Longitudinal Lab-Trend Analysis

**Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician.**

---

## Problem Statement

Every day, millions of lab reports are read the same way: "Is this value inside the green zone?" If yes — all clear. If no — flag it.

But this misses something clinically important: **the trend that happens entirely within the "normal" range.**

A patient's eGFR can drop from 68 → 52 over 18 months, never once falling below the 60 threshold that triggers a flag. A HbA1c can climb from 5.6% → 6.6%, spending months in the "normal" zone while the patient's metabolic health quietly deteriorates.

TrendSight was built to catch these hidden signals — by applying linear trend analysis to longitudinal lab data and communicating risk before a single value crosses into "abnormal" territory.

## Why Trend-Based (Longitudinal) Analysis Matters

In clinical practice, the difference between a one-time abnormal value and a developing trend is critical. Isolated spikes can be lab errors, transient illness, or medication timing. But a sustained trend — even entirely within the normal range — can signal the early stages of chronic kidney disease, prediabetes, or other conditions.

Current standard-of-care often relies on single-value thresholding. TrendSight demonstrates how simple, transparent statistical methods (linear regression over time) can add clinical signal without requiring expensive infrastructure or black-box AI.

## How It Works

1. **Synthetic Data Generation** — `data/generate_synthetic_patients.py` produces 4 realistic patient personas with longitudinal lab records over 12-24 months.

2. **Trend Analysis** — `engine/trend_analysis.py` computes linear regression (slope, R², rate of change per month) for each lab marker over time, and projects how many months until the value would cross a clinically meaningful threshold at the current slope.

3. **Risk Scoring** — `engine/risk_scoring.py` combines proximity to threshold and slope steepness into a transparent 0-10 Trend Risk Score, classified as **Low** 🟢, **Watch** 🟡, or **Elevated** 🔴.

4. **Access-Aware Recommendations** — `engine/access_aware_recommendations.py` adjusts follow-up advice based on patient access factors (transport, insurance, pharmacy access) using simple rules — not machine learning.

5. **Plain-Language Explanations** — `llm/explain.py` converts trend data into patient-friendly explanations with questions to ask a doctor. Works entirely offline via pre-populated demo cache; no API key required.

6. **Interactive Dashboard** — `app/streamlit_app.py` provides a dropdown-driven UI to explore all 4 personas.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Data | Python, NumPy, Pandas |
| Analysis | Linear regression (pure NumPy — no sklearn) |
| Scoring | Rules-based proximity + velocity formula |
| Charts | Matplotlib |
| UI | Streamlit |
| Explanations | Demo cache (pre-populated for all personas) |
| Deployment | Local — `streamlit run` |

## How to Run

```bash
# 1. Clone or navigate to the project
cd trendsight

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the checkpoint demo (optional — verifies everything works)
python3 checkpoint_demo.py

# 5. Launch the Streamlit app
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Optional: LLM API Integration

To use a live LLM for patient explanations, set an OpenAI-compatible API key:

```bash
export OPENAI_API_KEY="sk-..."
```

If no key is set, the app falls back to its pre-populated demo cache — the demo works identically either way.

## Project Structure

```
trendsight/
├── README.md
├── requirements.txt
├── checkpoint_demo.py          # Standalone verification of Steps 1-4
├── maria_trend_chart.png       # Generated example chart
├── data/
│   ├── generate_synthetic_patients.py
│   └── __init__.py
├── engine/
│   ├── trend_analysis.py
│   ├── risk_scoring.py
│   ├── access_aware_recommendations.py
│   └── __init__.py
├── app/
│   ├── streamlit_app.py
│   └── __init__.py
└── llm/
    ├── explain.py
    ├── prompt_templates.py
    ├── demo_cache.json
    └── __init__.py
```

## Personas

| Name | Age | Key Pattern | Expected Result |
|------|-----|------------|----------------|
| Maria | 54 | eGFR declining 68→52, creatinine rising 0.9→1.4 | 🔴 Elevated / 🟡 Watch |
| James | 39 | HbA1c rising 5.6→6.6 | 🟡 Watch |
| Aisha | 28 | All labs stable within range | 🟢 All Low |
| Robert | 61 | One acute potassium spike, otherwise flat | 🟢 All Low |

## Limitations

- **Risk thresholds are illustrative, not clinically validated.** The Trend Risk Score formula was designed for hackathon demonstration purposes. Consult a medical professional for real risk assessment.
- **All patient data is synthetic/generated.** No real patient data was used in any part of this system.
- **Linear trends are a simplification.** Real clinical data may have non-linear patterns, seasonal variation, and complex interactions not captured by simple linear regression.
- **Not a diagnostic device.** This tool is a demonstration of a data-science concept. It does not diagnose, treat, or manage any medical condition.
- **Access-aware recommendations are rules-based.** They use simple `if-then` logic on patient tags, not validated clinical guidelines. Always defer to a clinician's judgment.

## Disclaimers

> ⚠️ **Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician.**
>
> ⚠️ **Risk thresholds / rate constants are illustrative, not clinically validated.**
>
> ⚠️ **All patient data is synthetic/generated. Never use or reference real patient data.**

---

*Built for Vitalitics 2026 — a beginner-friendly health-tech data-science hackathon.*

## Status

Hackathon prototype — functional end to end on synthetic data, not clinically validated, not under active development beyond demos.

## License

[MIT](LICENSE)
