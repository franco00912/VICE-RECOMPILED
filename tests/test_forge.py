import tempfile
import unittest
import json
from pathlib import Path

import vice_recompiled


class PoolDiscoveryTests(unittest.TestCase):
    def test_package_and_pack_pools_map_without_reading_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game, work = root / "game", root / "work"
            a = game / "data" / "ttdb" / "maps" / "world.ttpf"
            b = game / "pack" / "story" / "data" / "ttdb" / "fx.ttpf"
            for path in (a, b):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic")
            completed = work / "assets" / "ttpf" / "world"
            completed.mkdir(parents=True)
            (completed / "manifest.json").write_text("{}", encoding="utf-8")

            rows = vice_recompiled.discover_pools(game, work)

            self.assertEqual(2, len(rows))
            self.assertTrue(rows[0].complete)
            self.assertEqual(str(work / "assets" / "ttpf_pack" / "story" / "fx"), rows[1].output_dir)
            self.assertFalse(rows[1].complete)

    def test_report_is_atomic_and_contains_no_file_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game, work, repo = root / "game", root / "work", root / "repo"
            for path in (game, work, repo):
                path.mkdir()
            pool = game / "secret.ttpf"
            pool.write_bytes(b"do-not-copy-this-payload")
            doc = vice_recompiled.status_document(game, work, repo)
            self.assertNotIn("do-not-copy", str(doc))
            self.assertEqual(1, doc["texture_pools"]["incomplete"])

    def test_comparison_detects_progress_and_regression(self):
        previous = {"revision": "old", "texture_pools": {"items": [
            {"relative_path": "kept.ttpf", "complete": True},
            {"relative_path": "finished.ttpf", "complete": False},
        ]}}
        current = {"revision": "new", "texture_pools": {"items": [
            {"relative_path": "kept.ttpf", "complete": False},
            {"relative_path": "finished.ttpf", "complete": True},
        ]}}
        comparison = vice_recompiled.compare_reports(previous, current)
        self.assertEqual(["finished.ttpf"], comparison["newly_completed_pools"])
        self.assertEqual(["kept.ttpf"], comparison["regressed_pools"])

    def test_atomic_write_replaces_complete_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "report.json"
            vice_recompiled.atomic_write(path, '{"ok": true}\n')
            self.assertEqual({"ok": True}, json.loads(path.read_text(encoding="utf-8")))
            self.assertFalse(path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
