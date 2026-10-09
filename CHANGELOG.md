# Changelog

## 0.1.0: 2026-10-09
First public release.
- Company profile: `setup_profile.py` drafts it from your website (logo rendered in isolation + auto light version, brand colour, fonts, contact, page text); `profile_check.py` validates it.
- Prospect audit (`audit.py`): Lighthouse, HTML/SEO, security headers and certificate (incl. bare-domain mismatch), links, tracking, social, conversion and ops signals; detects unreachable and parked domains.
- Scoring (`score.py`, `rubric.json`): 8 weighted categories; findings map to your offers through `mapping.yaml`.
- Two deck styles: "Neon Studio" (dark) and "Editorial" (light, serif). Photo backgrounds, number tiles, score and gaps, evidence screenshots, page-load filmstrip, product mockup, proof strip. One deck uses one brand.
- Prospect visuals (`prospect_assets.py`): their logo (background removed, light version for dark slides), their own photos, the Lighthouse load filmstrip. Generated on-brand backgrounds (`backgrounds.py`).
- Copy checks in `lint_deck.py`: stock phrases, em dashes, Title Case headlines and a repeated headline formula fail the build.
- Evidence capture (`evidence.py`) and free-photo fetching/search (`fetch_image.py`, Unsplash/Pexels).
- One send-ready PDF: flattened pages + invisible text layer + links, identical in WhatsApp/iOS/Android/email.
- `build.py`: deck lint (structure, word budget, fact-trace) → render → WCAG 2.2 AA + colour-blind sims → viewer compatibility (flat-structure check + Apple PDFKit / PDFium / poppler render diffs).
- `doctor.py`, Dockerfile, fictional end-to-end demo (`examples/run_demo.py`), unit tests, CI on Linux + macOS.
