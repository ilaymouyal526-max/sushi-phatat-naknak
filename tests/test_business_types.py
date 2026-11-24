import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from lead_agent import burn, business_types as bt, cli


class Playbook(unittest.TestCase):
    def test_all_types_complete_and_quadrants_match_research(self):
        types = bt.load()
        self.assertEqual(len(types), 18)
        for t in types:
            for k in ("id", "name", "he", "osm", "lo", "hi", "ease", "pitch", "pitch_he", "look", "must_have", "approach"):
                self.assertTrue(t.get(k), f"{t['id']} missing {k}")
        q = {t["id"]: t["quadrant"] for t in types}
        self.assertEqual({k for k, v in q.items() if v == "sweet"}, {"renovation", "zimmer", "aesthetic"})
        self.assertEqual({k for k, v in q.items() if v == "skip"}, {"garage"})
        self.assertEqual(q["lawyer"], "bigfish")
        self.assertEqual(q["barber"], "volume")

    def test_get_by_id_hebrew_and_alias(self):
        self.assertEqual(bt.get("zimmer")["id"], "zimmer")
        self.assertEqual(bt.get("צימרים")["id"], "zimmer")
        self.assertEqual(bt.get("Electrician")["id"], "trades")
        self.assertEqual(bt.get("רופא שיניים")["id"], "dentist")
        self.assertIsNone(bt.get("spaceship repair"))

    def test_name_filter_only_where_tags_are_shared(self):
        leads = [{"name": "קליניקת לייזר רונית"}, {"name": "ציפורניים של מאיה"}]
        self.assertEqual(len(bt.filter_by_name(bt.get("aesthetic"), leads)), 1)
        self.assertEqual(len(bt.filter_by_name(bt.get("beauty"), leads)), 2)


class SuggestAndFind(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"LEAD_AGENT_HOME": os.path.join(self.tmp.name, "leads"),
                                                "LEAD_BURN_STATE": os.path.join(self.tmp.name, "burn.json")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_suggest_one_per_quadrant_and_rotates(self):
        first = bt.suggest()
        self.assertEqual([s["quadrant"] for s in first], ["sweet", "volume", "bigfish"])
        burn.save({**burn.DEFAULTS, "runs": [{"finished": "2026-11-24T17:00", "target": {"type": first[0]["id"]}}]})
        again = bt.suggest()
        self.assertNotEqual(again[0]["id"], first[0]["id"])
        self.assertEqual(again[1]["id"], first[1]["id"])

    def test_find_with_type_uses_its_tags_filter_and_names_files(self):
        fake = [{"lead_id": f"osm:node/{i}", "name": n, "category": "shop=beauty", "city": "haifa", "address": "",
                 "phone": "", "email": "", "website": "", "facebook": "", "instagram": "", "directory_page": "",
                 "opening_hours": "", "lat": 32.8, "lon": 35.0}
                for i, n in [(1, "Laser Clinic Haifa"), (2, "Nails by Dana")]]
        out = StringIO()
        with mock.patch.object(cli.osm, "find_businesses", return_value=(fake, {})) as fb, redirect_stdout(out):
            cli.main(["find", "Haifa", "--type", "aesthetic", "--focus", "website", "--no-audit"])
        self.assertEqual(fb.call_args.args[1], bt.get("aesthetic")["osm"])
        res = json.loads(out.getvalue())
        self.assertEqual([l["name"] for l in res["top"]], ["Laser Clinic Haifa"])
        self.assertTrue(res["files"]["json"].endswith("-aesthetic-website.json"))
        self.assertEqual(res["business_type"]["quadrant"], "sweet")
        self.assertEqual(bt.history().get("aesthetic") is not None, True)

    def test_unknown_type_is_a_clear_error(self):
        with self.assertRaises(SystemExit) as cm, redirect_stdout(StringIO()):
            cli.main(["find", "Haifa", "--type", "spaceships"])
        self.assertIn("renovation", str(cm.exception))


if __name__ == "__main__":
    unittest.main()


class AppPlaybook(unittest.TestCase):
    def test_restaurant_quadrants(self):
        q = {t["id"]: t["quadrant"] for t in bt.load("app")}
        self.assertEqual(len(q), 14)
        self.assertEqual({k for k, v in q.items() if v == "sweet"}, {"pizza", "burger", "sushi", "shabbat", "healthy"})
        self.assertEqual(q["cafe"], "volume")
        self.assertEqual(q["chain"], "bigfish")
        self.assertEqual(q["catering"], "skip")
        self.assertEqual(bt.get("פיצה", "app")["id"], "pizza")
        self.assertIsNone(bt.get("pizza", "website"))

    def test_cuisine_or_name_and_branches(self):
        leads = [{"name": "Napoli", "cuisine": "pizza"}, {"name": "פיצה שמש", "cuisine": ""},
                 {"name": "Sushi Bar", "cuisine": "sushi;japanese"}, {"name": "Cafe X", "cuisine": ""}]
        self.assertEqual([l["name"] for l in bt.filter_by_name(bt.get("pizza", "app"), leads)], ["Napoli", "פיצה שמש"])
        self.assertEqual(len(bt.filter_by_name(bt.get("cafe", "app"), leads)), 4)  # no filter for plain cafés
        branches = [{"name": "Burger Bros"}, {"name": "burger  bros"}, {"name": "Solo"}]
        self.assertEqual(len(bt.filter_by_name(bt.get("chain", "app"), branches)), 2)

    def test_find_app_type_and_history_kept_apart(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {
                "LEAD_AGENT_HOME": os.path.join(tmp, "leads"), "LEAD_BURN_STATE": os.path.join(tmp, "b.json")}):
            fake = [{"lead_id": "osm:node/1", "name": "Napoli", "cuisine": "pizza", "category": "amenity=restaurant",
                     "city": "petah tikva", "address": "", "phone": "", "email": "", "website": "", "facebook": "",
                     "instagram": "", "directory_page": "", "opening_hours": "", "lat": 32.09, "lon": 34.88}]
            out = StringIO()
            with mock.patch.object(cli.osm, "find_businesses", return_value=(fake, {})), redirect_stdout(out):
                cli.main(["find", "Petah Tikva", "--focus", "app", "--type", "pizza", "--no-audit"])
            res = json.loads(out.getvalue())
            self.assertTrue(res["files"]["json"].endswith("-pizza-app.json"))
            self.assertIn("pizza", bt.history("app"))
            self.assertNotIn("pizza", bt.history("website"))
            self.assertNotIn("pizza", [s["id"] for s in bt.suggest("app")])
