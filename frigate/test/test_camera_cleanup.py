"""Tests for removing a deleted camera's media files."""

import os
import tempfile
import unittest
from unittest.mock import patch

from frigate.util import camera_cleanup

OWN = [
    "front-1700000000.123456-abc123.jpg",
    "front-1700000000.123456-abc123-clean.webp",
    "front-1700000000.123456-abc123-clean.png",
    os.path.join("review", "thumb-front-1700000002.5-ghi789.webp"),
]
# A second camera whose name starts with the deleted camera's name and a dash.
OTHER = [
    "front-door-1700000001.654321-def456.jpg",
    "front-door-1700000001.654321-def456-clean.webp",
    "front-door-1700000001.654321-def456-clean.png",
    os.path.join("review", "thumb-front-door-1700000003.25-jkl012.webp"),
]


class TestCleanupCameraFiles(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.clips = os.path.join(tmp.name, "clips")
        os.makedirs(os.path.join(self.clips, "review"))
        for name, path in (
            ("CLIPS_DIR", self.clips),
            ("RECORD_DIR", os.path.join(tmp.name, "recordings")),
            ("THUMB_DIR", os.path.join(tmp.name, "thumbs")),
        ):
            patcher = patch.object(camera_cleanup, name, path)
            patcher.start()
            self.addCleanup(patcher.stop)
        for name in OWN + OTHER:
            open(os.path.join(self.clips, name), "w").close()

    def remaining(self):
        return sorted(
            name
            for name in OWN + OTHER
            if os.path.exists(os.path.join(self.clips, name))
        )

    def test_deleting_a_camera_removes_its_media(self):
        camera_cleanup.cleanup_camera_files("front")
        self.assertEqual(self.remaining(), sorted(OTHER))

    def test_deleting_a_camera_keeps_media_of_a_camera_with_a_longer_name(self):
        camera_cleanup.cleanup_camera_files("front-door")
        self.assertEqual(self.remaining(), sorted(OWN))


if __name__ == "__main__":
    unittest.main()
