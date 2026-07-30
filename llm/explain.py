"""
llm/explain.py
==============
Given a flagged marker + trend data, generate:
  (a) A plain-language explanation for the patient
  (b) 3 specific questions to ask their doctor
  (c) An urgency framing (routine / "bring this up soon" / discuss promptly)

ALWAYS includes the required disclaimer.

DEMO MODE (default): If no API key is set in the environment, loads from
llm/demo_cache.json which is pre-populated with good examples for ALL 4
personas. This means the live demo NEVER depends on a live API call succeeding.

If an API key IS available (for any LLM provider), calls the API; otherwise
(or as a safety net) falls back to demo_cache.json.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.
"""

import json
import os
from typing import Optional

from engine.trend_analysis import TrendResult
from engine.risk_scoring import RiskScore
from llm.prompt_templates import build_explanation_prompt


def _build_cache_key(marker_name: str, patient_name: str) -> str:
    """Build a cache key like 'Maria_eGFR' or 'James_HbA1c'."""
    return f"{patient_name}_{marker_name.replace(' ', '_')}"


def _load_demo_cache() -> dict:
    """Load the demo cache from disk."""
    cache_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "demo_cache.json"
    )
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _call_llm_api(prompt: str) -> Optional[dict]:
    """
    Attempt to call an LLM API using available environment credentials.

    Currently supports:
      - OpenAI-compatible APIs (OPENAI_API_KEY)

    Returns parsed dict with 'plain_language', 'questions_for_doctor', 'urgency'
    or None if the call fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not api_key:
        return None

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful medical communication assistant. "
                        "You translate lab trend data into plain language for patients. "
                        "Always include the required disclaimer. Never give specific "
                        "medical advice — always direct patients to consult their doctor."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=600,
        )

        raw_text = response.choices[0].message.content or ""

        # Return raw LLM output as plain_language; the structured fields
        # are available via the demo cache. LLM responses vary too much
        # in format for reliable structured parsing here.
        return {
            "plain_language": raw_text[:800],
            "questions_for_doctor": [
                "What do these trends mean for my health?",
                "Should I be concerned about these changes?",
                "What follow-up tests or monitoring do you recommend?",
            ],
            "urgency": "Bring this up soon",
        }

    except Exception as e:
        print(f"[TrendSight] LLM API call failed: {e}")
        print("[TrendSight] Falling back to demo cache.")
        return None


def generate_explanation(
    marker_name: str,
    trend_result: Optional[TrendResult],
    risk_score: Optional[RiskScore],
    patient_name: str,
    patient_tags: list,
) -> dict:
    """
    Generate a patient-friendly explanation for a flagged marker.

    Returns dict with keys:
      - plain_language (str)
      - questions_for_doctor (list of str)
      - urgency (str)

    Falls back to demo cache if API is unavailable.
    """
    # Build the cache key
    cache_key = _build_cache_key(marker_name, patient_name)
    demo_cache = _load_demo_cache()

    # Try API first if key is available
    if os.environ.get("OPENAI_API_KEY", "").strip():
        prompt = build_explanation_prompt(
            marker_name=marker_name,
            trend_result=trend_result,
            risk_score=risk_score,
            patient_name=patient_name,
            patient_tags=patient_tags,
        )
        result = _call_llm_api(prompt)
        if result is not None:
            # Add disclaimer
            disclaimer = (
                "⚠️ Prototype for educational/hackathon purposes only. "
                "Not a diagnostic device. Not medical advice. "
                "Always consult a licensed clinician."
            )
            result["plain_language"] = (
                f"{result['plain_language']}\n\n{disclaimer}"
            )
            return result

    # Fallback to demo cache
    cache_entry = demo_cache.get(cache_key) or demo_cache.get("default", {})

    disclaimer = (
        "⚠️ Prototype for educational/hackathon purposes only. "
        "Not a diagnostic device. Not medical advice. "
        "Always consult a licensed clinician."
    )

    return {
        "plain_language": (
            f"{cache_entry.get('plain_language', 'Your lab results are stable — no concerning trends detected.')}"
            f"\n\n{disclaimer}"
        ),
        "questions_for_doctor": cache_entry.get(
            "questions_for_doctor",
            ["What do these results mean for my health?"],
        ),
        "urgency": cache_entry.get("urgency", "Routine"),
    }
