import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from lead_agent import cli

FAKE = [
    {"lead_id": "osm:node/1", "name": "מספרת דנה", "category": "shop=hairdresser", "city": "tel aviv",
     "address": "", "phone": "050-1", "email": "", "website": "", "facebook": "", "instagram": "",
     "directory_page": "", "opening_hours": "", "lat": 32.0, "lon": 34.7},
    {"lead_id": "osm:node/2", "name": "Kiosk", "category": "shop=kiosk", "city": "tel aviv",
     "address": "", "phone": "", "email": "", "website": "", "facebook": "", "instagram": "",
     "directory_page": "", "opening_hours": "", "lat": 32.0, "lon": 34.7},
]


class EndToEnd(unittest.TestCase):
    def test_find_merge_learn_with_default_home(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"LEAD_AGENT_HOME": tmp}), \
                mock.patch.object(cli.osm, "find_businesses", return_value=([dict(l) for l in FAKE], {})):
            out = StringIO()
            with redirect_stdout(out):
                cli.main(["find", "Tel Aviv"])
            result = json.loads(out.getvalue())
            self.assertEqual(result["stats"]["delivered"], 2)
            self.assertEqual(result["top"][0]["name"], "מספרת דנה")
            run = result["files"]["json"]

            upd = os.path.join(tmp, "u.json")
            with open(upd, "w", encoding="utf-8") as f:
                json.dump({"osm:node/1": {"outreach_he": "היי", "instagram": "dana"}}, f)
            with redirect_stdout(StringIO()):
                cli.main(["merge", run, upd])
            with open(run, encoding="utf-8") as f:
                lead = next(l for l in json.load(f)["leads"] if l["lead_id"] == "osm:node/1")
            self.assertEqual(lead["outreach_he"], "היי")
            self.assertIn("has_social", lead["signals"])

            # Phone-friendly layout: name first, only header row + name column frozen.
            from openpyxl import load_workbook
            ws = load_workbook(result["files"]["xlsx"]).active
            header = [c.value for c in ws[1]]
            self.assertEqual(header[0], "name / שם")
            self.assertEqual(ws.freeze_panes, "B2")
            for machine in ("status", "notes", "outreach_he", "signals", "lead_id"):
                self.assertIn(machine, header)
            self.assertTrue(str(ws.cell(row=2, column=3).value).startswith("Hot"))

            # Lead cards page: call + WhatsApp (mobile) with the opener prefilled.
            with open(result["files"]["html"], encoding="utf-8") as f:
                page = f.read()
            self.assertIn("מספרת דנה", page)

            # A second find skips leads already delivered.
            out = StringIO()
            with redirect_stdout(out), mock.patch.object(cli.osm, "find_businesses",
                                                         return_value=([dict(l) for l in FAKE], {})):
                cli.main(["find", "Tel Aviv", "--category", "beauty"])
            self.assertEqual(json.loads(out.getvalue())["stats"]["skipped_already_delivered"], 2)

            out = StringIO()
            with redirect_stdout(out):
                cli.main(["learn", result["files"]["xlsx"]])
            self.assertIn("note", json.loads(out.getvalue()))  # no statuses yet -> baseline kept


if __name__ == "__main__":
    unittest.main()
