import unittest

from lead_agent.cards import is_mobile, phone_e164, render_cards


class Phones(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(phone_e164("0546559181"), "972546559181")
        self.assertEqual(phone_e164("+972 3 774 5888"), "97237745888")
        self.assertEqual(phone_e164("054-655-9181"), "972546559181")
        self.assertEqual(phone_e164("00972 54 655 9181"), "972546559181")
        self.assertEqual(phone_e164(""), "")
        self.assertEqual(phone_e164("123"), "")

    def test_mobile(self):
        self.assertTrue(is_mobile("972546559181"))
        self.assertFalse(is_mobile("97237745888"))


class Cards(unittest.TestCase):
    def leads(self):
        return [
            {"lead_id": "a", "name": "מוסך <b>דני</b>", "phone": "054-655-9181", "band": "Hot", "success_pct": 8.8,
             "lead_type": "WEBSITE", "sell": "אתר חדש · New website", "why_he": "אין אתר; יש טלפון",
             "outreach_he": "היי דני, ראיתי שאין לכם אתר", "category": "shop=car_repair", "enriched": True,
             "website": "javascript:alert(1)", "instagram": "dani_garage"},
            {"lead_id": "b", "name": "Clinic", "phone": "03-774-5888", "band": "Cold", "success_pct": 1.6,
             "lead_type": "LOW_FIT", "category": "amenity=clinic"},
        ]

    def test_render(self):
        page = render_cards(self.leads(), {"city": "haifa", "category": "auto", "created": "2026-11-11T10:00"})
        self.assertIn('href="tel:+972546559181"', page)
        self.assertIn('href="tel:+97237745888"', page)
        self.assertEqual(page.count("https://wa.me/"), 1)  # landline gets no WhatsApp button
        self.assertIn("wa.me/972546559181?text=", page)
        self.assertIn("היי דני, ראיתי שאין לכם אתר", page)
        self.assertIn("https://www.instagram.com/dani_garage", page)
        self.assertNotIn("<b>דני</b>", page)  # names are escaped
        self.assertNotIn("javascript:", page)  # unsafe URLs dropped
        self.assertIn('data-band="Hot"', page)


if __name__ == "__main__":
    unittest.main()
