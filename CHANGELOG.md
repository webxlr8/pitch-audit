# Changelog

## 0.1.1 (2026-10-09)
Faster to a finished deck, one new finding.
- `prepare.py`: one command prepares a prospect. The audit runs in parallel with collecting their logo and photos, then the filmstrip, score and background. On a real site: 99 s across four commands down to 52 s in one.
- New finding: AI assistants blocked from reading the site. Checks ChatGPT search, ChatGPT browsing, Perplexity and Claude search, through robots.txt (read the way a browser reads it, to avoid false alarms on bot-protected sites) and through firewall/CDN blocks. Blocking training-only bots is reported but not penalised.
- Optional `compare` slide layout: a side-by-side table for package or option proposals (2–3 columns, checks, dashes or text). The default pitch still makes one recommendation.
- Evaluated and not adopted: brand-mention and citability scoring from other open-source SEO skills. They returned placeholder or low-signal results in our tests and would not help win a client.

## 0.1.0 (2026-10-09)
First public release.

Pitching
- Company profile set up from your own website (`setup_profile.py`): logo rendered alone with a light version made automatically, brand colour, fonts, contact, page text for drafting your offers. `profile_check.py` validates it.
- Prospect audit (`audit.py`): Lighthouse speed tests (mobile and desktop in parallel, via the PageSpeed API or local Lighthouse), SEO, security headers and certificates (including a bad certificate on the bare domain), links, analytics, social, conversion and operations signals. Detects unreachable and parked domains.
- Scoring (`score.py`, `rubric.json`): 8 weighted categories; findings map to your offers through `mapping.yaml`.
- Prospect visuals (`prospect_assets.py`): their logo with the background removed, their own photos, the page-load filmstrip. Evidence screenshots (`evidence.py`), free photo search (`fetch_image.py`), generated on-brand backgrounds (`backgrounds.py`).
- Two deck styles: Neon Studio (dark) and Editorial (light, serif).

Quality gates (`build.py`)
- Lint: every number traced to a source, word budget per slide, and copy checks that fail stock phrases, em dashes, Title Case headlines and a repeated headline formula.
- WCAG 2.2 AA contrast measured on the rendered pixels, including text over photos; colour-blind simulations.
- Viewer compatibility: every page must be one flat image; pages rendered in Apple PDFKit (macOS), PDFium and poppler (if installed) are compared with the design.

Light by default
- One PDF per prospect, about 1.5–2 MB for 8 slides (1920 px pages); `--hq` for 2560 px print quality.
- No poppler or Node.js required: PDF checks use PDFium and pypdf; speed tests can use Google's PageSpeed API.
- Apple PDFKit checker compiled once and cached.
- Shorter `SKILL.md`; details load only when needed.

Project
- Fictional end-to-end demo (`examples/run_demo.py`), 14 unit tests, CI on Linux and macOS, Dockerfile, `doctor.py`.
