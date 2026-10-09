---
name: pitch-audit
description: Turn any prospect's website into a short, visual pitch deck PDF from YOUR company. It audits the prospect's site (speed, SEO, mobile, trust, conversion, social, AI search, ops signals), researches their business, scores the gaps, maps them to your services or products, and renders one send-ready PDF that looks identical in WhatsApp and email, plus internal sales notes. First run sets up your company profile from your own website (logo, colours, fonts, services, contact). Use when the user wants to set up their company for pitching, or shares a prospect URL or lead list and asks to audit, analyse, pitch, prospect, or create a proposal/report/deck.
---

# pitch-audit: prospect website → audit → one visual pitch PDF

Two folders, two jobs:
- **This skill** (generic): audit, scoring, layouts, rendering, checks. It knows no company.
- **Your company profile** (`./pitch-profile/`, or `$PITCH_PROFILE`): who is pitching. Contains `company.yaml`, `catalog.yaml`, `mapping.yaml`, `proof.yaml`, `brand/` and an optional `theme.json`. Everything company-specific lives here.

**Skill folder** (`SKILL_DIR`): `${CLAUDE_PLUGIN_ROOT}/skills/pitch-audit` when installed as a plugin, or `.claude/skills/pitch-audit` when copied into a project. All `scripts/...` paths below are relative to it. Run them from the project root, where `pitch-profile/` and `clients/<slug>/` live.
Try it first: `python3 <SKILL_DIR>/../../examples/run_demo.py` (plugin repo) builds a full demo deck for a fictional company and prospect.

## Rules that shape every deck
1. **One deck = one brand: yours.** Products from your catalog appear by name and logo, in your colours. Never switch colours between slides.
2. **Fewest pages, most visuals, least text.** About 8 slides. Each has a headline ≤ 8 words, one line ≤ 15 words and one impact line ≤ 12. Every slide is anchored by a visual: a photo, their own screenshot, a big number, a score ring or a product mockup. Details go in the sales notes (`references/copy-voice.md`).
3. **One recommendation, one first step.** Later offers go in a single `next` line.
4. **Honest and kind.** Every number traces to the audit, scores, manual facts or your profile. Prices, guarantees and results only as written in `catalog.yaml` / `proof.yaml`. Critique the website, never the people.
5. **One file, perfect everywhere.** Flattened pages + a text layer + links. `build.py` must pass WCAG 2.2 AA and the PDFKit/poppler checks.

## Setup (once per machine)
Run `python3 scripts/doctor.py`. It checks everything and prints the exact install command for anything missing.
Needs Python 3.9+ (`pip install -r requirements.txt`), Google Chrome (or Playwright's bundled Chromium via `PITCH_BROWSER=chromium`), Node.js (`npx lighthouse@13`) and poppler. On macOS, `swift` adds the Apple PDFKit check.
Optional keys: `PSI_API_KEY` (PageSpeed fallback), `UNSPLASH_ACCESS_KEY` / `PEXELS_API_KEY` (photo search).
Alternatively, use the `Dockerfile` (everything preinstalled).

## Setup (once per company): `/pitch-audit setup <your-company-url>`
Run this if `pitch-profile/company.yaml` doesn't exist, or the user asks to set up or change their company.
1. `python3 scripts/setup_profile.py <url> [--assets <brand-folder>]`
   It reads the homepage and up to 8 key pages, then writes:
   - `company.yaml`: name, contact, booking link, social, accent colour, fonts, logo
   - `brand/`: the logo rendered from the site; a white version is auto-made if only a dark logo exists
   - `_sources/*.txt`: page text
   - `setup-report.md`: what was found and what is missing
   If the user has brand files (official white logo, fonts), pass `--assets <folder>`, or copy them into `pitch-profile/brand/` and point `company.yaml` at them.
2. **Draft from `_sources/`** (Claude): `catalog.yaml` (each real offer: id, name, type service|product, capabilities, promise, includes, first_step, price only if public, guarantees only if stated, logo for products), `mapping.yaml` (capability → offer, `fit_rules` with industry keywords, `guidance`), `proof.yaml` (stats, client names, case studies; `result` stays null unless the user confirms a real number).
3. Show the user a short summary of the draft profile and ask them to confirm or correct the offers, prices and proof. Never publish claims they haven't confirmed.
4. `python3 scripts/profile_check.py` must exit 0. Fix the FAILs and mention the WARNs.

## Workflow (per prospect)
1. **Audit** (~3 min, run in background): `python3 scripts/audit.py <url> --out clients/<slug>`. Exit 2 means unreachable or parked: confirm the URL. It also flags a wrong certificate on the bare domain.
2. **Research** (`references/business-research.md`) → `research.md`: what they do, customers, size signals, ops signals, who shows up instead of them in search.
3. **Manual facts + score**: write `manual.json` (`references/audit-rubric.md`) with verified facts and visual `extra_findings`, then run `python3 scripts/score.py clients/<slug>`. Fix false positives in `manual.json`, never in `scores.json`.
4. **One lead offer** using `references/offer-selection.md` and `mapping.yaml → guidance`.
5. **Visuals** (theirs first, see "Images" in `references/copy-voice.md`):
   - `python3 scripts/prospect_assets.py clients/<slug>` gives you:
     - their logo (`client.logo` / `client.logo_on_dark`, shown as "Prepared for" on the cover)
     - their own photos (`images/prospect-photo-N.jpg` plus a contact sheet; look and pick)
     - the Lighthouse page-load filmstrip (`images/filmstrip.json`, used as `finding.filmstrip`)
   - Evidence (`scripts/evidence.py`): proof from their own pages, 1000×700. Each run prints a deck-data `image` snippet; fill in its `alt`.
     - `--cert-warning`: the browser security interstitial.
     - `--text "..."` / `--selector`: a section or element.
     - `--clip`: a page area. `--mobile`: the phone view.
     - `--stack a.png b.png`: claim above reality.
   - Only if they have no usable photos: free photos via `scripts/fetch_image.py` (`--search` with API keys, or Unsplash/Pexels URLs). Match the industry and region; no other companies' logos; no faces.
   - Closing slide or filler: `scripts/backgrounds.py clients/<slug>` (generated on-brand topographic texture).
   - Never fake photos of their business. A missing photo never blocks: the slide falls back to the mockup or theme.
6. **deck-data.json** (`references/deck-data-schema.md` + the 8-slide outline and headline rules in `references/copy-voice.md`): cover → what we understood → score + 3 gaps → 3 gap slides → recommendation (product mockup with their data) → next step + proof strip. Sentence-case headlines in varied shapes, written about *this* prospect; the lint fails stock phrases, em dashes, Title Case and a repeated headline formula. **Pick the style**: `style-1` (dark, tech, logistics/SaaS) or `style-2` "Editorial" (light, serif; hospitality, food, professional services, traditional businesses): `"style": "style-2"` or `build.py ... --style style-2`. Give every `image` an `alt`. Use the client's region for currency and channel. In product mockups, use the label "Illustrative mockup".
7. **Build + verify**: `python3 scripts/build.py clients/<slug>`. It stops at the first failure:
   - **Lint**: deck structure; the word budget per slide; every number on a slide traced to the audit, scores, manual facts, research or profile (mockups exempt). A traced number proves it exists in a source, not that it's the right metric, so still check meaning.
   - **Render**.
   - **WCAG 2.2 AA**.
   - **Viewer compatibility**: a flat-page structure check that works on any OS, plus rendering in Apple PDFKit (macOS only, the WhatsApp/iOS engine), PDFium (Chrome/Android/Gmail) and poppler, diffed against the design.
   Then it prints the **one PDF to send**. Read every `previews/slide-XX.png` yourself: look for clipped text, empty areas, busy photo behind text, a single word alone on a line.
8. **Sales notes** (internal, never in the PDF): `sales-notes.md` with lead score + offer, decision maker, why now (3), objections → answers (3), first offer, follow-up email (< 150 words, attach the PDF), WhatsApp opener (< 50 words), risks and unknowns.
9. **Report**: send the PDF to the user (SendUserFile). Give the score, top 3 gaps, lead offer, lead score and any unverified items.

**Why the PDF is flattened:** Chrome exports CSS masks, filters and blur effects as soft masks and image tiles. Apple PDFKit (WhatsApp, Apple Mail, iOS) and Android viewers drop or misplace them. A page that is a single image can't be mis-drawn. Never send a vector "print to PDF" export.

## Batch
`python3 scripts/batch.py leads.csv --audit` (run in background) → steps 2–8 per client (subagents, max 4 in parallel) → `batch.py leads.csv --rank` → `clients/leads.csv`.

## Customising
- **Styles** = layouts (`styles/<name>/`): `style-1` "Neon Studio" (dark, default) and `style-2` "Editorial" (light, serif). See `styles/README.md`.
- **Themes** = your colours, fonts and logo, from the profile. See `themes/README.md`.
- **Scoring** weights: `references/rubric.json` (`python3 scripts/score.py --explain`).

## Hard rules
- Never invent metrics, follower counts, reviews, client results, prices or guarantees.
- Public data only. No logins, no bypassing bot protection, polite crawl speed.
- The deck goes to the prospect; sales notes and the profile's internal notes never do.
- Don't send anything that failed `build.py`.
