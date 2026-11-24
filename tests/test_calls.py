import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lead_agent import call_times, calls, plan

LEADS = [
    {"lead_id": "osm:node/1", "name": "מוסך", "category": "shop=car_repair", "phone": "054-1234567",
     "band": "Hot", "success_pct": 8.4, "lead_type": "WEBSITE", "signals": ["no_website"], "why_he": "אין אתר"},
    {"lead_id": "osm:node/2", "name": "מסעדה", "category": "amenity=restaurant", "phone": "03-1234567",
     "band": "Warm", "success_pct": 5.0, "lead_type": "WEBSITE", "signals": ["no_website"], "why_he": "אין אתר"},
    {"lead_id": "osm:node/3", "name": "צמיגים", "category": "shop=tyres", "phone": "04-7654321",
     "band": "Hot", "success_pct": 7.7, "lead_type": "WEBSITE", "signals": ["no_website"], "why_he": "אין אתר"},
    {"lead_id": "osm:node/4", "name": "בלי טלפון", "category": "shop=clothes", "phone": "",
     "band": "Hot", "success_pct": 9.0, "lead_type": "WEBSITE", "signals": ["no_website"], "why_he": "אין אתר"},
]
T = dt.datetime


class CallLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"LEAD_AGENT_HOME": self.tmp.name})
        self.env.start()
        Path(self.tmp.name, "run.json").write_text(json.dumps({"meta": {}, "leads": LEADS}, ensure_ascii=False),
                                                   encoding="utf-8")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_no_answer_retries_in_a_different_window(self):
        calls.add("osm:node/2", "no_answer", at=T(2026, 11, 17, 10, 15))  # restaurant, morning window
        fu = calls.follow_up(dict(LEADS[1]), calls.history_by_lead()["osm:node/2"], now=T(2026, 11, 17, 10, 20))
        self.assertEqual(fu["state"], "retry")
        self.assertEqual(fu["next"], T(2026, 11, 17, 15, 0))  # afternoon window, not the same morning one

    def test_stops_after_four_no_answers(self):
        for d in range(4):
            calls.add("osm:node/1", "no_answer", at=T(2026, 11, 15 + d, 13, 0))
        fu = calls.follow_up(dict(LEADS[0]), calls.history_by_lead()["osm:node/1"], now=T(2026, 11, 19, 9, 0))
        self.assertEqual(fu["state"], "stop")

    def test_callback_and_status(self):
        calls.add("osm:node/1", "call_back", at=T(2026, 11, 15, 13, 0), callback_at=T(2026, 11, 17, 14, 0))
        leads = [dict(l) for l in LEADS]
        calls.apply_to_leads(leads)
        self.assertEqual(leads[0]["follow_up_state"], "callback")
        self.assertEqual(leads[0]["status"], "replied")
        calls.add("osm:node/1", "won", at=T(2026, 11, 17, 14, 5))
        calls.apply_to_leads(leads)
        self.assertEqual(leads[0]["status"], "won")

    def test_not_interested_goes_to_do_not_contact(self):
        calls.add("osm:node/3", "not_interested", at=T(2026, 11, 15, 13, 0))
        dnc = calls.load_dnc()
        self.assertTrue(calls.is_dnc(LEADS[2], dnc))
        # same phone under another id is also blocked
        self.assertTrue(calls.is_dnc({"lead_id": "osm:node/99", "phone": "+972 4 765 4321"}, dnc))

    def test_import_dedupes(self):
        f = Path(self.tmp.name, "phone.csv")
        f.write_text("lead_id,at,result,callback_at,note,name,profile\n"
                     "osm:node/1,2026-11-15 13:00,no_answer,,,מוסך,garage\n"
                     "osm:node/1,2026-11-15 13:00,no_answer,,,מוסך,garage\n"
                     "osm:node/1,bad,no_answer,,,,\n", encoding="utf-8")
        self.assertEqual(calls.import_file(f), (1, 1))
        self.assertEqual(calls.import_file(f), (0, 2))

    def test_personal_best_hours(self):
        for i in range(12):  # garage owners answer at 15:00, not at 13:00
            calls.add("osm:node/1", "answered", at=T(2026, 11, 1 + i, 15, 10))
            calls.add("osm:node/1", "no_answer", at=T(2026, 11, 1 + i, 13, 10))
        stats = calls.personal_stats()
        self.assertEqual(stats["garage"]["top"][0], 15)
        lead = call_times.annotate({"category": "shop=car_repair"}, stats)
        self.assertIn("15:00-16:00", lead["call_personal"])


class DailyPlan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"LEAD_AGENT_HOME": self.tmp.name})
        self.env.start()
        Path(self.tmp.name, "run.json").write_text(json.dumps({"meta": {}, "leads": LEADS}, ensure_ascii=False),
                                                   encoding="utf-8")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_plan_order_slots_and_ics(self):
        calls.add("osm:node/2", "call_back", at=T(2026, 11, 15, 11, 0), callback_at=T(2026, 11, 17, 15, 30))
        calls.add("osm:node/3", "not_interested", at=T(2026, 11, 15, 11, 5))
        result = plan.build(dt.date(2026, 11, 17), now=T(2026, 11, 16, 20, 0))
        names = {e["lead"]["name"]: e for e in result["entries"]}
        self.assertNotIn("צמיגים", names)          # do not contact
        self.assertNotIn("בלי טלפון", names)       # can't call without a phone
        self.assertEqual(names["מסעדה"]["kind"], "callback")
        self.assertEqual(names["מסעדה"]["time"], T(2026, 11, 17, 15, 30))
        garage = names["מוסך"]["time"]
        self.assertTrue(T(2026, 11, 17, 12, 30) <= garage < T(2026, 11, 17, 15, 0))  # garage best window
        files = plan.write(result)
        ics = files["ics"].read_bytes().decode("utf-8")  # keep CRLF line endings
        self.assertIn("BEGIN:VCALENDAR", ics)
        self.assertIn("DTSTART:20261117T133000Z", ics.replace("\r\n ", ""))  # 15:30 Israel = 13:30 UTC
        self.assertIn("TRIGGER:-PT10M", ics)
        self.assertTrue(all(len(l.encode()) <= 75 for l in ics.split("\r\n")))
        self.assertIn("תוכנית שיחות", files["html"].read_text(encoding="utf-8"))

    def test_saturday_and_holidays_are_empty(self):
        self.assertEqual(plan.build(dt.date(2026, 11, 21), now=T(2026, 11, 20, 9, 0))["entries"], [])
        self.assertEqual(plan.next_workday(dt.date(2026, 11, 21)), dt.date(2026, 11, 22))
        self.assertEqual(plan.build(dt.date(2026, 9, 21), now=T(2026, 9, 20, 9, 0))["entries"], [])

    def test_today_only_future_slots(self):
        result = plan.build(dt.date(2026, 11, 17), now=T(2026, 11, 17, 13, 0))
        self.assertTrue(all(e["time"] >= T(2026, 11, 17, 13, 0) for e in result["entries"]))


if __name__ == "__main__":
    unittest.main()
