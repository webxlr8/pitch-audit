# Styles and themes

A style decides layout and composition. It lives in `skills/pitch-audit/styles/<name>/`. Two ship today:

- `style-1`, Neon Studio: dark canvas, faint grid, accent glows, heavy sans-serif headlines, glass cards. Suits tech, logistics and SaaS prospects.
- `style-2`, Editorial: light paper background, Fraunces serif headlines, white cards with soft shadows, the accent used sparingly. Suits hospitality, food, professional services and traditional businesses.

A theme supplies your colours, fonts and logo, and comes from your profile (see `themes/README.md`). Any style works with any theme. In light styles the generator darkens your accent until it passes WCAG AA on paper and on tinted cards.

Pick a style per deck with `"style": "style-2"` in `deck-data.json`, or `build.py clients/<slug> --style style-2`.

## Making a new style

Copy `style-2` (it only overrides CSS and reuses style-1's layouts), then edit `style.css` and `style.json`. Use theme CSS variables only. Don't position things with CSS transforms or use gradient-clipped text, because both render differently in PDF engines. A new style is ready when `python3 examples/run_demo.py` passes all four build steps with it.
