"""Run: python -m unittest discover -s tests   (from flowers/)"""
import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest import mock

from src import post as P


def _log(minutes_ago, dry=False):
    at = (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    return [{"at": at, "id": "x", "fp": "f", "post_id": "1", "dry_run": dry}]


class GuardTest(unittest.TestCase):
    def run_main(self, log, argv):
        fake_client = mock.MagicMock()
        fake_client.return_value.post.return_value = "NEW"
        with mock.patch("src.content.load_log", return_value=log), \
             mock.patch.object(P, "append_log") as app, \
             mock.patch.object(P, "ThreadsClient", fake_client), \
             mock.patch.object(P.config, "DRY_RUN", False), \
             mock.patch.object(P.config, "require_credentials", lambda: None):
            buf = io.StringIO()
            with redirect_stdout(buf):
                P.main(argv)
        return fake_client.return_value.post.called, buf.getvalue()

    def test_blocks_when_last_post_recent(self):
        posted, out = self.run_main(_log(80), [])
        self.assertFalse(posted)
        self.assertIn("GUARD", out)

    def test_only_without_force_is_blocked(self):
        posted, _ = self.run_main(_log(60), ["--only", P.load_posts()[0]["id"]])
        self.assertFalse(posted)

    def test_only_with_force_bypasses(self):
        posted, out = self.run_main(_log(60), ["--only", P.load_posts()[0]["id"], "--force"])
        self.assertTrue(posted)
        self.assertIn("bypassed", out)

    def test_posts_after_gap(self):
        posted, _ = self.run_main(_log(91), [])
        self.assertTrue(posted)

    def test_dry_run_entries_ignored(self):
        posted, _ = self.run_main(_log(10, dry=True), [])
        self.assertTrue(posted)


if __name__ == "__main__":
    unittest.main()
