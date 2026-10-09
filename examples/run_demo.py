#!/usr/bin/env python3
"""End-to-end demo: fictional seller (Northwind Studio) pitches a fictional prospect (Kestrel Valley Haulage).

    python3 examples/run_demo.py [--fast]     (--fast skips Lighthouse: no speed timings or filmstrip)

Starts the flawed demo site on 127.0.0.1:8765 → audit.py → score.py → evidence.py → fills deck-data.json from
the template using the audit's own numbers → build.py (lint, render, WCAG, viewer checks).
Output: examples/northwind/clients/kestrel-valley/*.pdf (also copied to examples/demo-output.pdf, which is git-ignored).
"""
import json
import os
import shutil
import subprocess
import sys

EX = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(EX)
SCRIPTS = os.path.join(ROOT, "skills", "pitch-audit", "scripts")
CLIENT = os.path.join(EX, "northwind", "clients", "kestrel-valley")
URL = f"http://127.0.0.1:{os.environ.get('DEMO_PORT', 8765)}/"


def run(*args):
    print("\n$ " + " ".join(os.path.basename(a) if a.endswith(".py") else a for a in args), flush=True)
    r = subprocess.run([sys.executable, *args], env={**os.environ, "PITCH_PROFILE": os.path.join(EX, "northwind", "pitch-profile")})
    if r.returncode != 0:
        sys.exit(f"step failed: {args[0]}")


def fill(template, values):
    s = json.dumps(template)
    for k, v in values.items():
        s = s.replace(f'"{{{{{k}:int}}}}"', str(v)).replace(f'"{{{{{k}}}}}"', json.dumps(v)).replace(f"{{{{{k}}}}}", str(v))
    return json.loads(s)


def main():
    sys.path.insert(0, os.path.join(EX, "demo-site"))
    import serve
    srv = serve.start(background=True)
    try:
        audit = [os.path.join(SCRIPTS, "audit.py"), URL, "--out", CLIENT]
        if "--fast" in sys.argv:
            audit.append("--no-lighthouse")
        run(*audit)
        run(os.path.join(SCRIPTS, "score.py"), CLIENT)
        run(os.path.join(SCRIPTS, "prospect_assets.py"), CLIENT, URL)   # their logo, their photos, load filmstrip
        run(os.path.join(SCRIPTS, "backgrounds.py"), CLIENT, "--count", "1")
        ev = os.path.join(SCRIPTS, "evidence.py")
        run(ev, CLIENT, URL, "--name", "band", "--selector", ".band div:first-child")
        run(ev, CLIENT, URL + "contact.html", "--name", "hours", "--selector", ".box p:first-child")
        run(ev, CLIENT, URL, "--name", "tracking", "--selector", ".band div:nth-child(2)")
        run(ev, CLIENT, "--name", "promise", "--stack", "evidence-tracking.png", "evidence-hours.png")
        a = json.load(open(os.path.join(CLIENT, "audit.json")))
        sc = json.load(open(os.path.join(CLIENT, "scores.json")))
        cats = [{"label": c["label"].replace(" Foundations", "").replace(" & Security", "").replace(" Visibility", "").replace(" Maturity", ""),
                 "score": c["score"]} for c in sc["categories"].values()]
        page_bytes = (a["lighthouse"]["mobile"] or {}).get("total_bytes") or a["page"]["page_bytes_hint"]
        values = {"url": URL, "overall": sc["overall"], "categories": cats, "page_mb": round(page_bytes / 1_000_000, 1)}
        fsp = os.path.join(CLIENT, "images", "filmstrip.json")
        # tell the blank-screen story only if the data shows one (≥ 2 s before anything appears)
        has_fs = os.path.exists(fsp) and (json.load(open(fsp)).get("first_content_s") or 0) >= 2
        if has_fs:
            fs = json.load(open(fsp))
            fr = fs["frames"]
            first = next(i for i, f in enumerate(fr) if not f["blank"])
            pick = sorted({0, max(0, first - 2), max(0, first - 1), first, len(fr) - 1})[-5:]
            values["first_content_s"] = fs["first_content_s"]
            values["filmstrip"] = {"frames": [{"src": fr[i]["src"], "label": f"{fr[i]['t_s']}s"} for i in pick],
                                   "highlight": pick.index(first), "caption": "Lighthouse mobile filmstrip (simulated slow 4G)"}
        tpl = json.load(open(os.path.join(CLIENT, "deck-data.template.json")))
        tpl["slides"] = [x for x in tpl["slides"] if x.get("use_if") in (None, "filmstrip" if has_fs else "no_filmstrip")]
        for x in tpl["slides"]:
            x.pop("use_if", None)
        deck = fill(tpl, values)
        json.dump(deck, open(os.path.join(CLIENT, "deck-data.json"), "w"), indent=2, ensure_ascii=False)
        run(os.path.join(SCRIPTS, "build.py"), CLIENT)
        pdf = next(f for f in os.listdir(CLIENT) if f.endswith(".pdf"))
        shutil.copy(os.path.join(CLIENT, pdf), os.path.join(EX, "demo-output.pdf"))
        print(f"\nDemo PDF: {os.path.join(EX, 'demo-output.pdf')}")
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
