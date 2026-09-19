from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class RepositoryStructureTests(unittest.TestCase):
    def test_required_agent_files_exist(self):
        required = [
            "app.py",
            "video_agent/producer.py",
            "video_agent/director.py",
            "video_agent/qc.py",
            "video_agent/generation.py",
            "vidgoclip/pipeline.py",
            "vidgoclip/exporter.py",
            "shorts_factory/video_generation.py",
            "shorts_factory/video_generators/comfyui_wan.py",
            "workflows/wan22_5b_t2v_api.json",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_settings_are_separate(self):
        clipper = (ROOT / "vidgoclip/config.py").read_text(encoding="utf-8")
        generator = (ROOT / "shorts_factory/config.py").read_text(encoding="utf-8")
        self.assertIn("clipper_settings.json", clipper)
        self.assertIn("generation_settings.json", generator)

    def test_wan_workflow_is_json_and_has_placeholders(self):
        workflow_path = ROOT / "workflows/wan22_5b_t2v_api.json"
        raw = workflow_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        self.assertIsInstance(data, dict)
        self.assertIn("__YT_SMB_PROMPT__", raw)
        self.assertIn("__YT_SMB_WIDTH__", raw)
        self.assertIn("__YT_SMB_HEIGHT__", raw)

    def test_manifest_contract_is_documented(self):
        docs = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("production_manifest.json", docs)
        self.assertIn("component scorecards", docs)


if __name__ == "__main__":
    unittest.main()
