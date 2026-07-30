# TrendSight — Video Script

**Total runtime: < 5 minutes**
**Format: Screen recording + voiceover**
**Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician.**

---

## [0:00 - 0:45] The Hook

> *(Screen: Single lab report, all values in green. Then a time-lapse overlay showing values slowly drifting.)*

**Voiceover:**
"Your labs came back. Everything's in the green. You're fine, right?

Not necessarily.

This is Maria. Her eGFR — a kidney health marker — dropped from 68 to 52 over 18 months. Every single reading was in the 'normal' range. But the *trend* tells a different story.

Most lab reports check one thing: 'Is this value out of range?' But by the time a value *is* out of range, you've often lost months of early signal.

TrendSight changes that."

---

## [0:45 - 1:30] The Problem & Solution

> *(Screen: Split view — traditional single-value check vs. TrendSight's trend view)*

**Voiceover:**
"The problem is simple: current standard-of-care predominantly uses single-value thresholding. Is eGFR above 60? Pass. Below 60? Flag.

But diseases don't work that way. Kidneys don't fail overnight. Blood sugar doesn't spike from normal to diabetic in a week.

TrendSight applies a simple, transparent technique: **linear regression over time.** For each lab marker, we compute:

- The slope — how fast is it changing?
- The R² — how consistent is the trend?
- The projected time until it would cross a threshold at the current rate.

Then we combine how close you are to the boundary with how fast you're moving toward it into a single, easy-to-read Trend Risk Score."

---

## [1:30 - 3:00] Live Demo — Two Contrasting Personas

> *(Screen: Streamlit app, selecting Maria)*

**Voiceover:**
"Let's see this in action. I'll open the TrendSight dashboard and select Maria.

*(Click Maria)*

Maria is 54, lives in a rural area with limited transport, and sees her PCP about twice a year.

Immediately, we see her eGFR is flagged as **Watch** and her creatinine as **Elevated**. Look at the chart — the green band is the normal range. Her values are still partially inside it, but the downward line is unmistakable. That's the hidden signal.

*(Click James)*

Now let's look at James. His HbA1c has been slowly climbing from 5.6% to 6.6% over two years. Still in the 'normal' range by most standards — but flagged as **Watch** by trend analysis. His doctor could have months of lead time to discuss diet and lifestyle changes before it ever becomes a problem.

*(Click Aisha)*

And this is equally important — Aisha. All her labs are stable. **No false alarms.** Her Trend Risk Scores are all Low. This isn't a system that flags everything; it only flags when there's a real trend."

---

## [3:00 - 3:30] Tech Deep-Dive (30 seconds)

> *(Screen: Code snippets — the linear regression formula and the risk scoring formula)*

**Voiceover:**
"Behind the scenes, the math is deliberately simple and transparent. It's just linear regression — the same technique you learn in introductory statistics. No machine learning, no black boxes.

The Trend Risk Score is the sum of two sub-scores: proximity (how close you are to the boundary) and velocity (how fast you're moving), mapped to Low, Watch, or Elevated.

Every formula is documented in the code with comments explaining exactly how it works."

---

## [3:30 - 4:15] Access-Aware Layer

> *(Screen: Back to the dashboard, showing the personalized recommendations panel)*

**Voiceover:**
"And here's the part I'm most excited about. The recommendations adapt to the patient's real-world circumstances.

Because Maria has limited transport and lives in a rural area, the system suggests telehealth instead of assuming an in-person visit is easy. It recommends asking about mail-in lab kits.

For James, who has insurance and easy pharmacy access, the recommendations are different — follow up at the next appointment, your pharmacy is close by.

This is a small, rules-based layer — explicitly *not* machine learning — but it makes the difference between a tool that works in theory and one that works in practice.

Health equity isn't just about having good medical knowledge. It's about making sure that knowledge is actionable for *everyone.*"

---

## [4:15 - 4:45] Impact Statement & Closing

> *(Screen: Text overlay on a simple, clean background)*

**Voiceover:**
"TrendSight connects a real data-science technique — linear trend analysis — to a real clinical gap: the silent drift that happens inside 'normal' ranges.

It's not trying to replace doctors or diagnose disease with AI. It's a simple, transparent tool that surfaces information that's already in the data but easy to overlook.

The goal is health equity: catching concerning trends earlier, communicating them clearly, and adapting recommendations to the real-world barriers that determine whether a patient can actually follow through.

This is a prototype — not medical advice, not a diagnostic device. But it shows what's possible when we shift from 'Is this value normal?' to 'Is this *trend* normal?'"

---

## [4:45 - 5:00] Final Disclaimer

> *(Screen: Full disclaimer text)*

**Voiceover:**
"Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician. All patient data is synthetic. Risk thresholds are illustrative, not clinically validated.

Thank you for watching."

---

## Production Notes

- **Total screen recording time:** ~4:30 of actual demo/tool — leaves buffer for intro/outro
- **Keep pace:** The demo section (1:30-3:00) is the most important — that's where judges see it working
- **Front-load the value:** By 1:30, the viewer should understand the problem and the core idea
- **Show Aisha's non-flag prominently:** It proves the system is discriminating, not just flagging everything
- **Audio:** Clear, measured pace. No background music competing with voiceover.
