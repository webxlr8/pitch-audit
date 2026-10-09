# Your company profile (`pitch-profile/`)

The skill knows nothing about your company until you create a profile. Keep it in your project root (or point `PITCH_PROFILE` at it). It is yours: never commit it to the pitch-audit repo.

```bash
python3 skills/pitch-audit/scripts/setup_profile.py https://your-company.com [--assets ./brand-files]
python3 skills/pitch-audit/scripts/profile_check.py
```

| File | What goes in it |
|---|---|
| `company.yaml` | name, website, tagline, region, currency, language, contact (email, phone, short address, booking URL), brand (logo files, accent colour, background, fonts) |
| `catalog.yaml` | every offer a prospect can say yes to: `id`, `name`, `type` (service/product), `capabilities` (which finding types it fixes), `promise`, `includes`, `first_step`, optional `price` (public only), `guarantees`, `logo` (products), `booking_url` |
| `mapping.yaml` | `capabilities:` capability → offer id (`web`, `design`, `app`, `infra`, `growth`, `automation`, `ops`); `fit_rules:` industry keywords → offer + fit score; `default_fit`; `guidance:` your rules for choosing the lead offer |
| `proof.yaml` | `stats`, `clients`, `case_studies` (`result` only when approved by the client), `how_we_work` |
| `brand/` | `logo_on_dark` (white/light, for dark slides; required), `logo` (dark), product logos, optional fonts |
| `theme.json` | optional hand-tuned theme; otherwise generated from `company.yaml → brand` |

## Logos and assets
- Setup renders your site's logo in isolation. If it's dark, it makes a light version (dark neutral parts turn white; brand colours stay).
- Have official files? Pass `--assets <folder>`: files named `*logo*white*` / `*logo*light*` become `logo_on_dark`, `*logo*dark*` becomes `logo`, and font files become `brand/fonts.css`. Or copy them into `brand/` and edit `company.yaml`.

## Colours
Set `brand.accent` (your main colour). The generated theme keeps the deck dark, lightens the accent only as much as WCAG AA requires, tones down very bright accents for background glows, and lightens grey text until it passes on every background.
