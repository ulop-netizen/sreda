"""Run: python -m unittest discover -s tests   (from flowers/)"""
import io
import os
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest import mock

from src import post as P


def _log(minutes_ago, dry=False):
    at = (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    return [{"at": at, "id": "x", "fp": "f", "post_id": "1", "dry_run": dry}]


class SlotMissingTest(unittest.TestCase):
    def test_open_when_a_due_slot_has_no_post(self):
        # 08:47 Europe/Warsaw (CEST) — first slot is due, nothing posted today.
        now = datetime(2026, 10, 16, 6, 47, tzinfo=timezone.utc)
        with mock.patch.object(P, "load_log", return_value=[]):
            full, why = P.slot_missing(now)
        self.assertFalse(full)
        self.assertEqual(why, "")

    def test_full_when_due_slots_already_posted(self):
        now = datetime(2026, 10, 16, 6, 47, tzinfo=timezone.utc)
        log = [{"at": "2026-10-16T06:20:00Z", "dry_run": False}]
        with mock.patch.object(P, "load_log", return_value=log):
            full, why = P.slot_missing(now)
        self.assertTrue(full)
        self.assertEqual(why, "SLOT: сегодня уже 1 пост(ов), слотов наступило 1 — пропускаю.")

    def test_dry_run_and_other_dates_do_not_fill_a_slot(self):
        # 11:47 Warsaw — two slots due; only one real post today counts.
        now = datetime(2026, 10, 16, 9, 47, tzinfo=timezone.utc)
        log = [
            {"at": "2026-10-16T06:20:00+00:00", "dry_run": True},
            {"dry_run": False},
            {"at": "2026-10-15T16:10:00+00:00", "dry_run": False},
            {"at": "2026-10-16T06:35:00+00:00", "dry_run": False},
        ]
        with mock.patch.object(P, "load_log", return_value=log):
            full, why = P.slot_missing(now)
        self.assertFalse(full)
        self.assertEqual(why, "")

    def test_before_first_slot_nothing_is_due(self):
        now = datetime(2026, 10, 16, 5, 0, tzinfo=timezone.utc)  # 07:00 Warsaw
        with mock.patch.object(P, "load_log", return_value=[]):
            full, why = P.slot_missing(now)
        self.assertTrue(full)
        self.assertEqual(why, "SLOT: сегодня уже 0 пост(ов), слотов наступило 0 — пропускаю.")

    def test_slots_follow_warsaw_local_time(self):
        # CET (UTC+1): 07:09 UTC is 08:09 Warsaw, 07:10 UTC is 08:10.
        early = datetime(2026, 1, 16, 7, 9, tzinfo=timezone.utc)
        due = datetime(2026, 1, 16, 7, 10, tzinfo=timezone.utc)
        with mock.patch.object(P, "load_log", return_value=[]):
            full_early, _ = P.slot_missing(early)
            full_due, _ = P.slot_missing(due)
        self.assertTrue(full_early)
        self.assertFalse(full_due)

    def _run_main(self, argv):
        fake_client = mock.MagicMock()
        fake_client.return_value.post.return_value = "NEW"
        with mock.patch("src.content.load_log", return_value=_log(200)), \
             mock.patch.object(P, "append_log"), \
             mock.patch.object(P, "ThreadsClient", fake_client), \
             mock.patch.object(P.config, "DRY_RUN", False), \
             mock.patch.object(P.config, "require_credentials", lambda: None):
            buf = io.StringIO()
            with redirect_stdout(buf):
                P.main(argv)
        return fake_client.return_value.post.called, buf.getvalue()

    def test_slot_mode_skips_when_full(self):
        with mock.patch.dict(os.environ, {"SLOT_MODE": "1"}), \
             mock.patch.object(P, "slot_missing", return_value=(True, "SLOT: full")) as sm:
            posted, out = self._run_main(["--only", P.load_posts()[0]["id"]])
        self.assertFalse(posted)
        self.assertIn("SLOT: full", out)
        sm.assert_called_once()

    def test_force_bypasses_slot_mode(self):
        with mock.patch.dict(os.environ, {"SLOT_MODE": "1"}), \
             mock.patch.object(P, "slot_missing", return_value=(True, "SLOT: full")) as sm:
            posted, out = self._run_main(["--only", P.load_posts()[0]["id"], "--force"])
        self.assertTrue(posted)
        self.assertNotIn("SLOT: full", out)
        sm.assert_not_called()


if __name__ == "__main__":
    unittest.main()
