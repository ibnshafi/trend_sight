# TrendSight — Build Status

## Self-Check Answers

1. **Does this clearly connect a real data-science technique to a real clinical use case, not just "AI diagnoses disease"?**
   Yes — linear trend analysis over longitudinal lab values is a well-established clinical monitoring technique. TrendSight applies it to catch clinically meaningful decline *before* a single value crosses into abnormal territory, which is a real gap in current care.

2. **Would a non-technical judge understand the value in the first 60 seconds of the described video?**
   Yes — the hook is "the lab said 'normal' but something is changing." The Maria demo makes it instantly visual: a green reference band with a clear downward line inside it.

3. **Is there a moment that's genuinely different from a generic "predict disease X with sklearn" project?**
   Yes — Aisha's correct non-flag (all labs stable) proves the system doesn't just flag everything. The access-aware recommendations layer customizes follow-up advice based on real-world barriers (rural transport, insurance status).

4. **Are the disclaimers visible on every relevant screen, not buried once?**
   Yes — the Streamlit sidebar and every LLM response include the disclaimer.

5. **Does everything described in the video script actually exist and run in the submitted source?**
   Yes — every module runs end-to-end. See video_script.md for the script.

6. **Is the video script's total runtime under 5 minutes?**
   Yes — the script is designed with timestamps totaling under 5 minutes.

---

## Per-Step Status

- ✅ Step 1 done — synthetic data generator produces 4 personas (Maria, James, Aisha, Robert) with 10-15 visits each, correct trends, and access tags.
- ✅ Step 2 done — trend analysis computes slope, R², rate/month, and projected months-until-threshold for each marker. Tested on all 4 personas.
- ✅ Step 3 done — risk scoring combines proximity-to-threshold and slope velocity into Low/Watch/Elevated. Maria → Creatinine Elevated, eGFR Watch. James → HbA1c Watch. Aisha → All Low. Robert → All Low (spike isolated).
- ✅ Step 4 done — chart produced (maria_trend_chart.png) showing Maria's eGFR declining within the normal reference band with annotated insight.
- ✅ Step 5 done — Streamlit app with persona selector, trend charts, risk panel, and disclaimer working end-to-end.
- ✅ Step 6 done — LLM explain module with demo cache for all 4 personas. Works identically with or without API key.
- ✅ Step 7 done — Access-aware recommendations engine adjusts advice based on transport, insurance, and pharmacy access tags. Wired into Streamlit UI.
- ✅ README done — problem statement, how it works, tech stack, how to run, limitations, disclaimers.
- ✅ video_script.md done — timestamped script under 5 minutes covering hook, problem, solution, live demo, tech deep-dive, impact.
