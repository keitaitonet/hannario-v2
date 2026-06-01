import tempfile
import unittest
from pathlib import Path

from scripts.operator_backup_inventory import human_size, is_secret_path, scan_path


class OperatorBackupInventoryTest(unittest.TestCase):
    def test_scan_missing_path(self):
        item = scan_path(Path("missing-file"))

        self.assertFalse(item.exists)
        self.assertEqual(item.kind, "missing")
        self.assertEqual(item.size_bytes, 0)
        self.assertEqual(item.file_count, 0)

    def test_scan_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "local.sqlite3"
            path.write_bytes(b"abc")

            item = scan_path(path)

        self.assertTrue(item.exists)
        self.assertEqual(item.kind, "file")
        self.assertEqual(item.size_bytes, 3)
        self.assertEqual(item.file_count, 1)

    def test_scan_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "a.log").write_bytes(b"abc")
            (root / "nested").mkdir()
            (root / "nested" / "b.log").write_bytes(b"defg")

            item = scan_path(root)

        self.assertTrue(item.exists)
        self.assertEqual(item.kind, "dir")
        self.assertEqual(item.size_bytes, 7)
        self.assertEqual(item.file_count, 2)

    def test_secret_path_detection(self):
        self.assertTrue(is_secret_path(Path(".env")))
        self.assertTrue(is_secret_path(Path(".env.letta")))
        self.assertFalse(is_secret_path(Path("logs")))

    def test_human_size(self):
        self.assertEqual(human_size(12), "12 B")
        self.assertEqual(human_size(2048), "2.0 KiB")


if __name__ == "__main__":
    unittest.main()
