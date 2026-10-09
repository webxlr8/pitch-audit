# Scoring

`skills/pitch-audit/references/rubric.json` holds the weights; `score.py` applies them. Print the current table:
```bash
python3 skills/pitch-audit/scripts/score.py --explain
```
Eight categories (weights sum to 100): Performance 20, SEO 15, Mobile & UX 15, Trust & Security 10, Conversion 15, Social 10, AI Search 5, Operations 10. Each starts at 100 and loses points per failed check. Overall below 60 = "Needs attention" (shown in the deck), 60–79 = "Room to grow", 80+ = "Strong".

**Lead score** = 0.6 × (100 − overall) + 0.4 × fit, where fit comes from `mapping.yaml → fit_rules` (or `manual.json → fit`). High = big gap and strong fit with what you sell.

Speed timings (LCP, TBT) come from Lighthouse: Google's PageSpeed Insights API when `PSI_API_KEY` is set, or local Lighthouse when Node.js is installed (`--speed psi|local`). Mobile and desktop run in parallel. With `--speed off`, performance is scored from server response time and page weight only. Tune the weights for your market; keep `manual.json` for verified facts the scripts can't see (social activity, search presence, extra findings).
