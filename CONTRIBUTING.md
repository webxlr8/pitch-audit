# Contributing

Thanks for helping. A few rules keep pitch-audit trustworthy:

1. **No company data in the skill.** Everything about a seller lives in a profile folder; the skill stays generic. Examples use fictional companies only, and never real prospects.
2. **Never invent numbers.** New slide types must work with `lint_deck.py`'s fact-trace; new findings must cite evidence from `audit.json`.
3. **Every PDF must stay viewer-safe.** Run `python3 examples/run_demo.py`; all four build steps must pass. Decorative effects belong in the style's background layers; never position with CSS transforms or use gradient-clipped text.
4. **Accessibility is a floor.** Text ≥ 4.5:1 (large ≥ 3:1) on the real rendered pixels; graphics ≥ 3:1.

## Dev loop
```bash
python3 skills/pitch-audit/scripts/doctor.py
python3 -m unittest discover tests -v
python3 examples/run_demo.py
```

## Adding a style
Copy `skills/pitch-audit/styles/style-1` to `style-2`, change `style.css` / `layouts.py`, document it in `style.md`, add it to `styles/README.md`, and make the demo pass with `--style style-2`.

## Pull requests
Small and focused, with a before/after preview image for anything visual. Describe what you tested.
