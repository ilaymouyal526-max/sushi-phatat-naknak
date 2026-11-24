import re
import tempfile
import unittest
from pathlib import Path

from lead_agent import cards, export, services


def lead(category="shop=hairdresser", lead_type="WEBSITE", signals=None, lead_id="osm:node/1"):
    return {"lead_id": lead_id, "name": "Test", "category": category, "city": "tel aviv", "phone": "050-1234567",
            "lead_type": lead_type, "band": "Hot", "success_pct": 8.0, "signals": signals or ["no_website"],
            "why": "x", "call_profile": "beauty"}


class TestCatalog(unittest.TestCase):
    def test_every_reference_resolves(self):
        cat, f = services.catalog(), services.facts()
        for sid, s in cat["services"].items():
            for fid in s["facts"]:
                self.assertIn(fid, f["facts"], f"{sid} -> fact {fid}")
            for lid in s["legal"]:
                self.assertIn(lid, f["legal"], f"{sid} -> legal {lid}")
            if s["price"]:
                self.assertIn(s["price"], f["prices"], f"{sid} -> price {s['price']}")
        for g, grp in cat["groups"].items():
            for sid in grp["services"]:
                self.assertIn(sid, cat["services"], f"group {g} -> {sid}")
        for key, g in cat["map"].items():
            self.assertIn(g, cat["groups"], key)

    def test_every_number_and_law_has_a_source(self):
        f = services.facts()
        for sec, when in (("facts", "year"), ("legal", "checked"), ("prices", "year")):
            for k, v in f[sec].items():
                self.assertTrue(v.get("source"), f"{sec}.{k} source")
                self.assertTrue(re.match(r"https?://", v.get("url", "")), f"{sec}.{k} url")
                self.assertTrue(v.get(when), f"{sec}.{k} {when}")


class TestPicking(unittest.TestCase):
    def test_groups(self):
        self.assertEqual(services.group_for(lead("shop=hairdresser")), "hair")
        self.assertEqual(services.group_for(lead("shop=tattoo")), "tattoo")
        self.assertEqual(services.group_for(lead("amenity=spa")), "massage")
        self.assertEqual(services.group_for(lead("shop=cosmetics")), "beauty")
        self.assertEqual(services.group_for(lead("amenity=dentist")), "default")

    def test_no_website_puts_site_and_booking_first(self):
        top = [s["id"] for s in services.top_services(lead())]
        self.assertEqual(top[:2], ["site", "booking"])
        self.assertEqual(len(top), 3)

    def test_unknown_group_still_offers_something(self):
        top = services.top_services(lead("amenity=dentist", lead_type="AUTOMATION", signals=["has_phone"]))
        self.assertEqual(len(top), 3)

    def test_pack_has_all_four_kinds(self):
        pk = services.pack("tattoo")
        self.assertTrue(pk["services"] and pk["facts"] and pk["legal"] and pk["questions_he"])
        self.assertIn("consent_form", [s["id"] for s in pk["services"]])


class TestOutputs(unittest.TestCase):
    def test_cards_show_upsell_and_sheet(self):
        leads = [lead(), lead("shop=tattoo", lead_id="osm:node/2")]
        for l in leads:
            export.add_links(l)
        html = cards.render_cards(leads, {"city": "tel aviv", "category": "beauty", "created": "2026-11-24"})
        self.assertIn("להציע גם", html)
        self.assertIn('id="pack-hair"', html)
        self.assertIn('id="pack-tattoo"', html)
        self.assertIn('data-pack="tattoo"', html)
        self.assertIn("hbr.org", html)
        self.assertNotRegex(html, r"\b(prompt|confirm|alert)\(")

    def test_xlsx_has_column_and_sheet(self):
        from openpyxl import load_workbook
        leads = [lead()]
        for l in leads:
            export.add_links(l)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.xlsx"
            export.write_xlsx(leads, path)
            wb = load_workbook(path)
            self.assertIn("דף שיחה · Call sheet", wb.sheetnames)
            headers = [c.value for c in wb.worksheets[0][1]]
            self.assertIn("להציע גם / upsell", headers)
            col = headers.index("להציע גם / upsell") + 1
            self.assertIn("אתר עמוד אחד", wb.worksheets[0].cell(row=2, column=col).value)
            kinds = {r[1] for r in wb["דף שיחה · Call sheet"].iter_rows(min_row=2, values_only=True)}
            self.assertTrue({"🧰 שירות", "📊 מספר", "❓ שאלה", "⚖️ חוק"} <= kinds)


if __name__ == "__main__":
    unittest.main()
