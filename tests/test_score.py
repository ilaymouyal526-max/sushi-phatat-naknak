import json
import unittest
from unittest import mock

from lead_agent import learn, score
from lead_agent.osm import element_to_lead, resolve_categories

BASE = json.loads(score.BASELINE.read_text(encoding="utf-8"))


def pct(lead):
    return score.score_lead(dict(lead), BASE)["success_pct"]


class Scoring(unittest.TestCase):
    def test_prior_is_about_one_and_a_half_percent(self):
        z, _ = score.contributions([], BASE)
        self.assertAlmostEqual(100 * score.sigmoid(z), 1.5, delta=0.1)

    def test_best_no_website_lead_is_hot_but_realistic(self):
        lead = {"name": "Dr. Levi", "category": "amenity=dentist", "phone": "03-555",
                "facebook": "fb.com/x", "opening_hours": "Su-Th 09:00-18:00", "audit": {"site_status": "none"}}
        r = score.score_lead(lead, BASE)
        self.assertEqual(r["lead_type"], "WEBSITE")
        self.assertEqual(r["band"], "Hot")
        self.assertTrue(7 <= r["success_pct"] <= 15, r["success_pct"])

    def test_modern_site_scores_low(self):
        lead = {"name": "Noa", "category": "shop=hairdresser", "phone": "050", "website": "https://noa.co.il",
                "audit": {"site_status": "ok", "https": True, "has_viewport": True, "copyright_year": 2026,
                          "has_booking": True, "has_whatsapp": True, "has_form": True}}
        r = score.score_lead(lead, BASE)
        self.assertIn("modern_complete", r["signals"])
        self.assertEqual(r["lead_type"], "LOW_FIT")
        self.assertLess(r["success_pct"], 3.5)

    def test_broken_site_is_capped(self):
        many = {"name": "Old", "category": "shop=hairdresser", "phone": "03", "website": "http://old.co.il",
                "audit": {"site_status": "ok", "https": False, "has_viewport": False, "copyright_year": 2012,
                          "load_seconds": 6, "free_builder": True}}
        r = score.score_lead(many, BASE)
        self.assertEqual(r["lead_type"], "REDESIGN+AUTOMATION")
        self.assertLessEqual(r["success_pct"], 15)

    def test_unreachable_lead_is_cold(self):
        lead = {"name": "Ghost", "category": "shop=clothes", "audit": {"site_status": "none"}}
        self.assertEqual(score.score_lead(lead, BASE)["band"], "Cold")

    def test_low_value_category(self):
        a = {"name": "K", "category": "shop=kiosk", "phone": "1", "audit": {"site_status": "none"}}
        b = {"name": "K", "category": "shop=clothes", "phone": "1", "audit": {"site_status": "none"}}
        self.assertLess(pct(a), pct(b))


class BlockedSite(unittest.TestCase):
    def test_bot_blocked_site_is_not_dead_or_unreachable(self):
        lead = {"name": "X", "category": "shop=clothes", "website": "https://x.co.il",
                "audit": {"site_status": "blocked"}}
        sig = score.extract_signals(lead)
        self.assertNotIn("site_dead", sig)
        self.assertNotIn("no_website", sig)
        self.assertNotIn("no_contact", sig)


class Learning(unittest.TestCase):
    def test_fit_moves_weights_toward_evidence(self):
        # no_website leads win often, automation-only leads never do.
        samples = ([(["no_website", "has_phone"], 1)] * 6 + [(["no_website", "has_phone"], 0)] * 14
                   + [(["no_booking_or_whatsapp", "has_phone"], 0)] * 30)
        fitted = learn.fit(samples, BASE, steps=1500)
        self.assertGreater(fitted["features"]["no_website"]["weight"], BASE["features"]["no_website"]["weight"])
        self.assertLess(fitted["features"]["no_booking_or_whatsapp"]["weight"],
                        BASE["features"]["no_booking_or_whatsapp"]["weight"])

    def test_labels(self):
        self.assertEqual(learn.label_for("won"), 1)
        self.assertEqual(learn.label_for("Lost"), 0)
        self.assertIsNone(learn.label_for("meeting"))

    def test_learn_needs_enough_outcomes(self):
        with mock.patch.object(learn, "load_outcomes", return_value={}):
            self.assertIn("note", learn.learn(None))


class Osm(unittest.TestCase):
    def test_chain_excluded_and_social_website_moved(self):
        chain = {"type": "node", "id": 1, "tags": {"name": "Aroma", "amenity": "cafe", "brand": "Aroma"}}
        self.assertIsNone(element_to_lead(chain, "tel aviv"))
        el = {"type": "node", "id": 2, "lat": 32.0, "lon": 34.7,
              "tags": {"name": "מספרת דנה", "shop": "hairdresser", "website": "https://facebook.com/dana"}}
        lead = element_to_lead(el, "tel aviv")
        self.assertEqual(lead["website"], "")
        self.assertEqual(lead["facebook"], "https://facebook.com/dana")
        self.assertEqual(lead["category"], "shop=hairdresser")

    def test_directory_page_is_not_a_website_and_hospitals_excluded(self):
        el = {"type": "node", "id": 3, "tags": {"name": "Lucky Dog", "shop": "pet_grooming",
                                                 "website": "https://easy.co.il/page/123"}}
        lead = element_to_lead(el, "ramat gan")
        self.assertEqual(lead["website"], "")
        self.assertEqual(lead["directory_page"], "https://easy.co.il/page/123")
        hosp = {"type": "way", "id": 4, "tags": {"name": "Sheba", "healthcare": "hospital"}}
        self.assertIsNone(element_to_lead(hosp, "ramat gan"))

    def test_categories(self):
        self.assertIn("hairdresser", resolve_categories("beauty")["shop"])
        self.assertEqual(resolve_categories("dentist")["amenity"], ["dentist"])
        self.assertIn("craft", resolve_categories("all"))


if __name__ == "__main__":
    unittest.main()
