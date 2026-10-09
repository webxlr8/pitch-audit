"""Fast checks that need no browser: python3 -m unittest discover tests -v"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "pitch-audit", "scripts")
PROFILE = os.path.join(ROOT, "examples", "northwind", "pitch-profile")
sys.path.insert(0, SCRIPTS)
import profile as P  # noqa: E402


def run(script, *args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True)


class LintDeck(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        json.dump({"overall": 58}, open(os.path.join(self.d, "scores.json"), "w"))
        open(os.path.join(self.d, "research.md"), "w").write("Founded 2011. Fleet of 14 tankers. Homepage weighs 13,355,740 bytes.")

    def tearDown(self):
        shutil.rmtree(self.d)

    def deck(self, slides):
        json.dump({"title": "t", "slides": slides}, open(os.path.join(self.d, "deck-data.json"), "w"))
        return run("lint_deck.py", self.d, "--profile", PROFILE)

    def test_traced_numbers_pass(self):
        r = self.deck([{"layout": "statement", "title": "Built By Drivers.", "tiles": [{"value": "2011", "label": "Founded"}, {"value": "13.4 MB", "label": "page"}]},
                       {"layout": "offer", "title": "Portal.", "facts": [{"value": "$3,000", "label": "setup"}]}])
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_invented_number_fails(self):
        r = self.deck([{"layout": "statement", "title": "Built By Drivers.", "tiles": [{"value": "1999", "label": "Founded"}]}])
        self.assertEqual(r.returncode, 1)
        self.assertIn('"1999" not found', r.stdout)

    def test_mockup_numbers_are_exempt(self):
        r = self.deck([{"layout": "offer", "title": "Portal.", "mockup": {"kpis": [{"value": "987", "label": "loads"}]}}])
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_long_headline_fails(self):
        r = self.deck([{"layout": "statement", "title": "This Headline Has Far Too Many Words To Read On A Slide At A Glance"}])
        self.assertEqual(r.returncode, 1)
        self.assertIn("words (limit 8)", r.stdout)

    def test_unknown_layout_fails(self):
        self.assertEqual(self.deck([{"layout": "carousel", "title": "x"}]).returncode, 1)


class Slop(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def lint(self, slides):
        json.dump({"title": "t", "slides": slides}, open(os.path.join(self.d, "deck-data.json"), "w"))
        return run("lint_deck.py", self.d, "--profile", PROFILE)

    def test_stock_phrase_fails(self):
        r = self.lint([{"layout": "center", "title": "Unlock your *growth opportunities*"}])
        self.assertEqual(r.returncode, 1)
        self.assertIn("generic phrase", r.stdout)

    def test_em_dash_fails(self):
        r = self.lint([{"layout": "center", "title": "Slow site", "body": "Visitors leave — fast."}])
        self.assertIn("em dash", r.stdout)

    def test_repeated_formula_and_title_case_fail(self):
        t = ["Fast Store.\n*Slow Site.*", "Great Product.\n*Invisible Online.*", "Booked By Phone.\n*Tracked By Hope.*"]
        r = self.lint([{"layout": "center", "title": x} for x in t])
        self.assertIn("same 'Claim. *Payoff.*' formula", r.stdout)
        self.assertIn("Title Case", r.stdout)

    def test_varied_sentence_case_passes(self):
        t = ["What shippers see\n*before they call you*", "“Live tracking”\n*or office hours?*", "Fourteen tankers,\n*one phone line*"]
        r = self.lint([{"layout": "center", "title": x} for x in t])
        self.assertEqual(r.returncode, 0, r.stdout)


class Speed(unittest.TestCase):
    def test_source_selection(self):
        import audit as A
        old = dict(os.environ)
        try:
            os.environ.pop("PSI_API_KEY", None)
            self.assertEqual(A.speed_source("auto", "http://127.0.0.1:8765/"), "local")  # PageSpeed can't reach localhost
            os.environ["PSI_API_KEY"] = "x"
            self.assertEqual(A.speed_source("auto", "https://example.com"), "psi")
            self.assertEqual(A.speed_source("local", "https://example.com"), "local")
        finally:
            os.environ.clear(); os.environ.update(old)


class Profile(unittest.TestCase):
    def test_demo_profile_is_usable(self):
        r = run("profile_check.py", "--profile", PROFILE)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_mapping_to_unknown_offer_fails(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copytree(PROFILE, os.path.join(d, "p"))
            mp = os.path.join(d, "p", "mapping.yaml")
            with open(mp) as f:
                txt = f.read().replace("growth: growth", "growth: does-not-exist")
            with open(mp, "w") as f:
                f.write(txt)
            r = run("profile_check.py", "--profile", os.path.join(d, "p"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("unknown offer `does-not-exist`", r.stdout)
        finally:
            shutil.rmtree(d)

    def test_bright_accent_theme_passes_wcag(self):
        th = P.theme_from_company({"brand": {"accent": "#E8FF3A", "background": "#0B0B0B"}}, PROFILE)
        v = th["vars"]
        for k in ("--accent", "--muted", "--body"):
            self.assertGreaterEqual(P.contrast(v[k], v["--bg"]), 4.5, k)


class PdfStructure(unittest.TestCase):
    def test_flat_pdf_passes_and_masked_pdf_fails(self):
        import compat_check as C
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
        d = tempfile.mkdtemp()
        try:
            flat = Image.new("RGB", (400, 225), (20, 20, 20))
            flat.save(os.path.join(d, "flat.jpg"))
            c = canvas.Canvas(os.path.join(d, "flat.pdf"), pagesize=(400, 225))
            c.drawImage(ImageReader(os.path.join(d, "flat.jpg")), 0, 0, 400, 225)
            c.showPage(); c.save()
            self.assertEqual(C.structure_check(os.path.join(d, "flat.pdf")), [])
            rgba = Image.new("RGBA", (200, 100), (255, 0, 0, 128))  # alpha -> soft mask, like Chrome's CSS masks
            rgba.save(os.path.join(d, "mask.png"))
            c = canvas.Canvas(os.path.join(d, "masked.pdf"), pagesize=(400, 225))
            c.drawImage(ImageReader(os.path.join(d, "flat.jpg")), 0, 0, 400, 225)
            c.drawImage(ImageReader(os.path.join(d, "mask.png")), 50, 50, 200, 100, mask="auto")
            c.showPage(); c.save()
            self.assertTrue(C.structure_check(os.path.join(d, "masked.pdf")))
            import a11y_check as A  # PDF metadata checks work without poppler
            info = A.pdf_checks(os.path.join(d, "flat.pdf"))
            self.assertEqual(info["pages"], 1)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
