import unittest
from pathlib import Path

from lead_agent.audit import analyse_html, normalise_url

FIX = Path(__file__).parent / "fixtures"


class AnalyseHtml(unittest.TestCase):
    def test_old_site(self):
        r = analyse_html((FIX / "old_site.html").read_text(encoding="utf-8"), "http://yossi.co.il/")
        self.assertFalse(r["has_viewport"])
        self.assertEqual(r["copyright_year"], 2014)
        self.assertFalse(r["has_booking"])
        self.assertFalse(r["has_whatsapp"])
        self.assertFalse(r["has_form"])
        self.assertFalse(r["has_tel_link"])
        self.assertEqual(r["generator"], "FrontPage 4.0")

    def test_modern_site(self):
        r = analyse_html((FIX / "modern_site.html").read_text(encoding="utf-8"), "https://noa.co.il/")
        self.assertTrue(r["has_viewport"])
        self.assertEqual(r["copyright_year"], 2026)
        self.assertTrue(r["has_booking"])
        self.assertTrue(r["has_whatsapp"])
        self.assertTrue(r["has_form"])
        self.assertTrue(r["has_tel_link"])
        self.assertTrue(r["has_analytics"])
        self.assertFalse(r["free_builder"])

    def test_free_builder_and_hebrew_booking_text(self):
        r = analyse_html("<p>הזמנת תור בקלות</p>", "https://someone.wixsite.com/salon")
        self.assertTrue(r["free_builder"])
        self.assertTrue(r["has_booking"])

    def test_normalise_url(self):
        self.assertEqual(normalise_url("www.example.co.il"), "https://www.example.co.il")
        self.assertEqual(normalise_url(" http://a.com "), "http://a.com")
        self.assertEqual(normalise_url(""), "")


if __name__ == "__main__":
    unittest.main()
