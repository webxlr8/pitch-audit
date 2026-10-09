#!/usr/bin/env python3
"""Check this machine can run pitch-audit, and say exactly how to fix anything missing.

Usage:
    python3 doctor.py [--profile pitch-profile]
Exit code 1 if anything REQUIRED is missing.
"""
import importlib
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS = platform.system()  # Darwin | Linux | Windows

PY_DEPS = [("playwright", "playwright"), ("PIL", "pillow"), ("numpy", "numpy"), ("reportlab", "reportlab"),
           ("pypdf", "pypdf"), ("yaml", "pyyaml"), ("pypdfium2", "pypdfium2")]


def install_hint(tool):
    return {
        "poppler": {"Darwin": "brew install poppler", "Linux": "sudo apt-get install -y poppler-utils",
                    "Windows": "choco install poppler   (or scoop install poppler)"},
        "node": {"Darwin": "brew install node", "Linux": "sudo apt-get install -y nodejs npm",
                 "Windows": "winget install OpenJS.NodeJS"},
        "chrome": {"Darwin": "install Google Chrome, or: python3 -m playwright install chromium",
                   "Linux": "python3 -m playwright install --with-deps chromium",
                   "Windows": "install Google Chrome, or: py -m playwright install chromium"},
    }[tool].get(OS, "")


def check(label, ok, fix="", required=True):
    tag = "OK  " if ok else ("FAIL" if required else "WARN")
    print(f"  {tag} {label}" + ("" if ok else f"\n         fix: {fix}"))
    return ok or not required


def main():
    print(f"pitch-audit doctor · {OS} · Python {platform.python_version()}")
    good = True
    good &= check("Python ≥ 3.9", sys.version_info >= (3, 9), "install Python 3.9+")
    missing = []
    for mod, pkg in PY_DEPS:
        try:
            importlib.import_module(mod)
        except Exception:  # noqa: BLE001
            missing.append(pkg)
    good &= check("Python packages", not missing,
                  f"{sys.executable} -m pip install {' '.join(missing)}   (or: pip install -r requirements.txt)")

    chrome = False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            for kw in ({"channel": "chrome"}, {}):
                try:
                    p.chromium.launch(**kw).close()
                    chrome = kw.get("channel", "bundled chromium")
                    break
                except Exception:  # noqa: BLE001
                    continue
    except Exception:  # noqa: BLE001
        pass
    good &= check(f"Chrome for rendering ({chrome or 'none'})", bool(chrome), install_hint("chrome"))
    if chrome == "bundled chromium":
        print("         note: using Playwright's bundled Chromium (set PITCH_BROWSER=chromium); Google Chrome is preferred")

    good &= check("Node.js + npx (Lighthouse speed tests)", bool(shutil.which("npx")), install_hint("node"))
    good &= check("poppler (pdftoppm, pdftotext, pdfinfo)", bool(shutil.which("pdftoppm") and shutil.which("pdfinfo")), install_hint("poppler"))
    if OS == "Darwin":
        check("swift (Apple PDFKit check = WhatsApp/iOS engine)", bool(shutil.which("swift")),
              "xcode-select --install", required=False)
    else:
        print("  INFO Apple PDFKit check only runs on macOS; the structure check guarantees WhatsApp-safe PDFs everywhere")
    check("PSI_API_KEY (PageSpeed fallback when Lighthouse fails)", bool(os.environ.get("PSI_API_KEY")),
          "optional: create a key at https://developers.google.com/speed/docs/insights/v5/get-started", required=False)
    check("UNSPLASH_ACCESS_KEY or PEXELS_API_KEY (photo search via API)",
          bool(os.environ.get("UNSPLASH_ACCESS_KEY") or os.environ.get("PEXELS_API_KEY")),
          "optional: without keys, photos are fetched by URL or a generated background is used", required=False)

    sys.path.insert(0, HERE)
    import profile as P
    arg = sys.argv[sys.argv.index("--profile") + 1] if "--profile" in sys.argv else None
    d = P.find_profile_dir(arg)
    if d:
        r = subprocess.run([sys.executable, os.path.join(HERE, "profile_check.py"), "--profile", d], capture_output=True, text=True)
        good &= check(f"company profile ({d})", r.returncode == 0, "see: python3 scripts/profile_check.py")
    else:
        check("company profile", False, "python3 scripts/setup_profile.py <your-company-url>", required=False)

    print("\nReady." if good else "\nNot ready: fix the FAIL lines above.")
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
