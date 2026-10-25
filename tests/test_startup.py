import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from main import claim_instance


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux desktop integration")
class InstanceTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"DISPLAY": f"test-{os.getpid()}"})
        environment.start()
        self.addCleanup(environment.stop)

    def test_second_launch_signals_existing_process_and_exits(self):
        with claim_instance() as listener:
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            connection, _ = listener.accept()
            connection.close()

    def test_close_releases_instance_without_stale_files(self):
        claim_instance().close()
        claim_instance().close()

    def test_process_exit_releases_instance(self):
        result = subprocess.run(
            [sys.executable, "-c", "from main import claim_instance; s = claim_instance()"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        claim_instance().close()
