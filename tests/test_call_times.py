import datetime as dt
import unittest

from lead_agent import call_times as ct
from lead_agent import holidays


def sched(category, hours=""):
    return ct.annotate({"category": category, "opening_hours": hours})


class Profiles(unittest.TestCase):
    def test_restaurant_rush_is_mealtimes(self):
        lead = sched("amenity=restaurant")
        self.assertEqual(lead["call_profile"], "restaurant")
        self.assertIn("12:00-14:30", lead["call_avoid"])
        self.assertIn("18:30-21:30", lead["call_avoid"])
        tue = dt.date(2026, 11, 17)
        best, avoid, _, _ = ct.day_windows(lead["call_schedule"], tue)
        self.assertTrue(ct.in_ranges(best, 10 * 60 + 30))
        self.assertTrue(ct.in_ranges(avoid, 13 * 60))

    def test_trades_use_mobile_hours_not_shop_hours(self):
        lead = sched("craft=electrician", "Su-Th 08:00-17:00")
        self.assertEqual(lead["call_profile"], "trades")
        self.assertIn("07:30-08:30", lead["call_best"])  # before the shop opens: fine, it's a mobile
        self.assertIsNone(lead["call_schedule"]["open"])

    def test_bar_gets_first_half_hour_after_opening_and_never_friday_evening(self):
        lead = sched("amenity=bar", "Mo-Sa 19:00-02:00")
        s = lead["call_schedule"]
        self.assertEqual(s["best"][1], [[19 * 60, 19 * 60 + 30]])
        self.assertEqual(s["best"][5], [])  # Friday evening = Shabbat eve
        self.assertEqual(s["best"][0], [])  # closed on Sunday

    def test_beauty_busy_thursday_and_no_friday(self):
        s = sched("shop=hairdresser")["call_schedule"]
        self.assertEqual(s["best"][4], [])
        self.assertEqual(s["best"][5], [])

    def test_accountant_avoids_vat_days(self):
        lead = sched("office=accountant")
        self.assertIn("15", lead["call_tip"])
        best, _, _, note = ct.day_windows(lead["call_schedule"], dt.date(2026, 12, 13))
        self.assertEqual(best, [])
        self.assertIn("מע", note)

    def test_saturday_never(self):
        s = sched("amenity=restaurant")["call_schedule"]
        best, _, _, note = ct.day_windows(s, dt.date(2026, 11, 21))
        self.assertEqual(best, [])
        self.assertIn("שבת", note)

    def test_next_good_after_rush(self):
        s = sched("amenity=restaurant")["call_schedule"]
        self.assertEqual(ct.next_good(s, dt.datetime(2026, 11, 17, 12, 45)), dt.datetime(2026, 11, 17, 15, 0))
        self.assertEqual(ct.next_good(s, dt.datetime(2026, 11, 21, 10, 0)), dt.datetime(2026, 11, 22, 10, 0))

    def test_schedule_survives_json_round_trip(self):
        import json
        s = json.loads(json.dumps(sched("amenity=restaurant")["call_schedule"]))
        best, _, _, _ = ct.day_windows(s, dt.date(2026, 11, 17))
        self.assertTrue(best)


class OpeningHours(unittest.TestCase):
    def test_parse(self):
        h = ct.parse_opening_hours("Su-Th 09:00-19:00; Fr 09:00-14:00")
        self.assertEqual(h[0], [[540, 1140]])
        self.assertEqual(h[5], [[540, 840]])
        self.assertEqual(h[6], [])
        self.assertEqual(ct.parse_opening_hours("24/7")[3], [[0, 1440]])
        self.assertEqual(ct.parse_opening_hours("Mo-Fr 08:00-12:00,16:00-19:00; Sa off")[1],
                         [[480, 720], [960, 1140]])
        self.assertIsNone(ct.parse_opening_hours("by appointment"))
        self.assertIsNone(ct.parse_opening_hours(""))

    def test_hebrew(self):
        self.assertEqual(ct.hours_he("Su-Th 7:30-17:00; Fr 7:30-13:00"),
                         "א'–ה' 07:30-17:00 | ו' 07:30-13:00 | סגור: ש'")

    def test_closed_day_has_no_best_window(self):
        s = sched("shop=clothes", "Mo-Th 10:00-19:00")["call_schedule"]
        self.assertEqual(s["best"][0], [])  # Sunday closed
        self.assertTrue(s["best"][1])


class Holidays(unittest.TestCase):
    def test_known_dates(self):
        self.assertEqual(holidays.on(dt.date(2026, 9, 21))["kind"], "closed")      # Yom Kippur
        self.assertEqual(holidays.on(dt.date(2027, 4, 21))["kind"], "eve")         # Erev Pesach
        self.assertEqual(holidays.on(dt.date(2026, 9, 28))["kind"], "low")         # Chol HaMoed Sukkot
        self.assertEqual(holidays.on(dt.date(2027, 5, 11))["kind"], "sensitive")   # Yom HaZikaron
        self.assertIsNone(holidays.on(dt.date(2026, 11, 17)))

    def test_holiday_eve_behaves_like_friday(self):
        s = sched("amenity=restaurant")["call_schedule"]
        best, _, _, note = ct.day_windows(s, dt.date(2027, 4, 21))
        self.assertTrue(all(e <= 11 * 60 for _, e in best))
        self.assertIn("ערב פסח", note)
        self.assertEqual(ct.day_windows(s, dt.date(2026, 9, 21))[0], [])


if __name__ == "__main__":
    unittest.main()
