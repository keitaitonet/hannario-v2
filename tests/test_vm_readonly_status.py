import unittest

from scripts.vm_readonly_status import build_remote_script


class VmReadonlyStatusTest(unittest.TestCase):
    def test_remote_script_is_read_only_status_probe(self):
        script = build_remote_script("/srv/hannario-v2", 25)

        self.assertIn("## identity", script)
        self.assertIn("## system", script)
        self.assertIn("## commands", script)
        self.assertIn("## repo", script)
        self.assertIn("## user-systemd", script)
        self.assertIn("## docker", script)
        self.assertIn("/srv/hannario-v2", script)
        self.assertIn("-n 25", script)

    def test_remote_script_avoids_write_or_privileged_commands(self):
        script = build_remote_script("/srv/hannario-v2", 25)

        forbidden = [
            "sudo",
            "apt ",
            "install",
            "mkdir",
            "cp ",
            "rm ",
            "systemctl --user restart",
            "systemctl --user enable",
            "docker compose up",
            "docker compose down",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, script)


if __name__ == "__main__":
    unittest.main()
