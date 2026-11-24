import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from lead_agent import app_profile, burn, cli


def biz(i, website=""):
    return {"lead_id": f"osm:node/{i}", "name": f"B{i}", "category": "shop=hairdresser", "city": "tel aviv",
            "address": "", "phone": "050-1234567", "email": "", "website": website, "facebook": "", "instagram": "",
            "directory_page": "", "opening_hours": "", "lat": 32.0, "lon": 34.7}


GOOD_SITE = {"site_status": "ok", "https": True, "has_viewport": True, "copyright_year": 2026,
             "has_booking": True, "has_whatsapp": True, "has_form": True, "has_tel": True, "load_seconds": 0.5}


def fake_audit(leads):
    for l in leads:
        if l["website"]:
            l["audit"] = dict(GOOD_SITE) if "good" in l["website"] else {"site_status": "dead"}
        else:
            l["audit"] = {"site_status": "none"}


class Focus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {
            "LEAD_AGENT_HOME": os.path.join(self.tmp.name, "leads"),
            "LEAD_BURN_STATE": os.path.join(self.tmp.name, "burn.json"),
            "LEAD_APP_PROFILE": os.path.join(self.tmp.name, "app.json")})
        self.env.start()
        self.no_repo_profile = mock.patch.object(app_profile, "candidates",
                                                 lambda: [os.environ["LEAD_APP_PROFILE"] and
                                                          __import__("pathlib").Path(os.environ["LEAD_APP_PROFILE"])])
        self.no_repo_profile.start()

    def tearDown(self):
        self.no_repo_profile.stop()
        self.env.stop()
        self.tmp.cleanup()

    def run_find(self, *extra, leads=None):
        leads = leads or [biz(1), biz(2, "http://good.example"), biz(3, "http://dead.example")]
        out = StringIO()
        with mock.patch.object(cli.osm, "find_businesses", return_value=([dict(l) for l in leads], {})), \
                mock.patch.object(cli.audit, "audit_many", side_effect=fake_audit), redirect_stdout(out):
            cli.main(["find", "Tel Aviv", *extra])
        return json.loads(out.getvalue())

    def test_website_focus_keeps_only_no_site_or_dead_site(self):
        res = self.run_find("--focus", "website")
        self.assertEqual(sorted(l["lead_id"] for l in res["top"]), ["osm:node/1", "osm:node/3"])
        self.assertEqual(res["stats"]["skipped_has_working_website"], 1)
        self.assertTrue(res["files"]["json"].endswith("-website.json"))

    def test_app_focus_waits_for_profile(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_find("--focus", "app")
        self.assertIn("handoff", str(cm.exception))
        self.assertFalse(app_profile.status()["ready"])

    def test_app_focus_uses_profile_and_its_own_seen_list(self):
        self.run_find("--focus", "website")  # delivers 1 and 3 as website leads
        with open(os.environ["LEAD_APP_PROFILE"], "w", encoding="utf-8") as f:
            json.dump({"app_name": "X", "what_it_does": "y", "categories": "beauty", "good_signs": ["z"]}, f)
        with mock.patch.object(cli.osm, "find_businesses", return_value=([biz(1), biz(2)], {})) as fb, \
                mock.patch.object(cli.audit, "audit_many", side_effect=fake_audit), redirect_stdout(StringIO()) as out:
            cli.main(["find", "Tel Aviv", "--focus", "app"])
        self.assertEqual(fb.call_args.args[1], "beauty")
        res = json.loads(out.getvalue())
        self.assertEqual(sorted(l["lead_id"] for l in res["top"]), ["osm:node/1", "osm:node/2"])
        self.assertTrue(res["files"]["json"].endswith("-app.json"))
        # a second website run skips what the first delivered
        self.assertEqual(self.run_find("--focus", "website")["top"], [])

    def test_burn_memory_is_per_focus_but_dnc_is_shared(self):
        st = {**burn.DEFAULTS, "seen": [burn.hash_id("osm:node/1")], "dnc": [burn.hash_id("osm:node/2")]}
        self.assertEqual(burn.remembered("osm:node/1", st, "website"), "seen")
        self.assertIsNone(burn.remembered("osm:node/1", st, "app"))
        self.assertEqual(burn.remembered("osm:node/2", st, "app"), "dnc")


if __name__ == "__main__":
    unittest.main()
