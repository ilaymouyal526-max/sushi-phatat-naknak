import datetime as dt
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

from lead_agent import burn, cli

IL = burn.IL


def il(y, mo, d, h, mi):
    return dt.datetime(y, mo, d, h, mi, tzinfo=IL).timestamp()


RESET = il(2026, 11, 24, 17, 20)


class Decide(unittest.TestCase):
    def test_early_in_window_waits_until_70_minutes_before(self):
        r = burn.decide(il(2026, 11, 24, 12, 30), RESET, "allowed")
        self.assertEqual(r["action"], "wait")
        self.assertEqual(r["next_check"], int(RESET - 70 * 60))
        self.assertEqual(r["next_check_il"], "Tue 16:10")

    def test_notify_near_reset_with_usage_left(self):
        r = burn.decide(il(2026, 11, 24, 16, 10), RESET, "allowed")
        self.assertEqual(r["action"], "notify")
        self.assertEqual(r["deadline_il"], "Tue 17:15")
        self.assertEqual(r["target"]["city"], "tel aviv")
        # next check: 70 min before the end of a window that starts at the reset
        self.assertEqual(r["next_check"], int(RESET + 230 * 60))

    def test_warning_or_overage_skips(self):
        now = il(2026, 11, 24, 16, 10)
        self.assertEqual(burn.decide(now, RESET, "allowed_warning")["action"], "skip")
        self.assertEqual(burn.decide(now, RESET, "allowed", overage=True)["action"], "skip")

    def test_too_late_quiet_hours_already_asked_and_off(self):
        self.assertEqual(burn.decide(il(2026, 11, 24, 17, 0), RESET, "allowed")["action"], "skip")
        late = il(2026, 11, 25, 1, 30)
        r = burn.decide(late - 60 * 60, late, "allowed")
        self.assertEqual((r["action"], r["reason"]), ("skip", "quiet hours"))
        now = il(2026, 11, 24, 16, 10)
        self.assertEqual(burn.decide(now, RESET, "allowed", state={"asked_for": int(RESET)})["action"], "wait")
        self.assertEqual(burn.decide(now, RESET, "allowed", state={"enabled": False})["action"], "off")

    def test_no_reset_time_rechecks_later(self):
        now = il(2026, 11, 24, 9, 0)
        r = burn.decide(now, None, "allowed")
        self.assertEqual(r["action"], "wait")
        self.assertGreater(r["next_check"], now)


class StateAndMemory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"LEAD_BURN_STATE": os.path.join(self.tmp.name, "burn.json"),
                                                "LEAD_AGENT_HOME": os.path.join(self.tmp.name, "leads")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_finish_stores_hashes_not_lead_data_and_advances(self):
        run = Path(self.tmp.name) / "run.json"
        run.write_text(json.dumps({"leads": [
            {"lead_id": "osm:node/1", "name": "מספרת דנה", "phone": "050-1234567", "band": "Hot",
             "verified_online": "yes"},
            {"lead_id": "osm:node/2", "name": "Kiosk", "band": "Warm"}]}), encoding="utf-8")
        dnc = Path(self.tmp.name) / "dnc.csv"
        dnc.write_text("lead_id,name,phone,date\nosm:node/9,X,+972501234567,2026-11-20\n", encoding="utf-8")
        out = burn.finish(run, int(RESET), {"city": "tel aviv", "category": "beauty"}, dnc)
        self.assertEqual(out["recorded"]["hot"], 1)
        self.assertEqual(out["next_target"]["index"], 1)
        text = burn.state_path().read_text(encoding="utf-8")
        for secret in ("דנה", "050", "972", "osm:node", "Kiosk"):
            self.assertNotIn(secret, text)
        self.assertEqual(burn.remembered("osm:node/1"), "seen")
        self.assertEqual(burn.remembered("osm:node/9"), "dnc")
        self.assertIsNone(burn.remembered("osm:node/3"))

    def test_find_skips_remembered_leads(self):
        burn.save({**burn.DEFAULTS, "seen": [burn.hash_id("osm:node/1")], "dnc": [burn.hash_id("osm:node/2")]})
        fake = [{"lead_id": f"osm:node/{i}", "name": f"B{i}", "category": "shop=hairdresser", "city": "tel aviv",
                 "address": "", "phone": "", "email": "", "website": "", "facebook": "", "instagram": "",
                 "directory_page": "", "opening_hours": "", "lat": 32.0, "lon": 34.7} for i in (1, 2, 3)]
        out = StringIO()
        with mock.patch.object(cli.osm, "find_businesses", return_value=(fake, {})), redirect_stdout(out):
            cli.main(["find", "Tel Aviv", "--no-audit"])
        res = json.loads(out.getvalue())
        self.assertEqual([l["lead_id"] for l in res["top"]], ["osm:node/3"])
        self.assertEqual(res["stats"]["skipped_already_delivered"], 1)
        self.assertEqual(res["stats"]["skipped_do_not_contact"], 1)

    def test_cli_set_and_asked(self):
        with redirect_stdout(StringIO()):
            cli.main(["burn", "set", "--verify-count", "25", "--quiet", "22:00-09:00"])
            cli.main(["burn", "asked", str(int(RESET))])
        st = burn.load()
        self.assertEqual((st["verify_count"], st["quiet_hours"], st["asked_for"]),
                         (25, ["22:00", "09:00"], int(RESET)))


if __name__ == "__main__":
    unittest.main()
