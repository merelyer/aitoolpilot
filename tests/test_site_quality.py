import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://merelyer.github.io/aitoolpilot"


class SiteQualityTests(unittest.TestCase):
    def test_required_static_pages_exist(self):
        self.assertTrue((ROOT / "site" / "privacy" / "index.html").exists())
        self.assertTrue((ROOT / "site" / "affiliate-disclosure" / "index.html").exists())

    def test_seo_files_use_current_github_pages_url(self):
        sitemap = (ROOT / "site" / "sitemap.xml").read_text(encoding="utf-8")
        robots = (ROOT / "site" / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"{SITE_URL}/sitemap.xml", robots)
        self.assertIn(f"{SITE_URL}/", sitemap)
        self.assertNotIn("https://aitoolpilot.com", sitemap)
        self.assertNotIn("https://aitoolpilot.com", robots)

    def test_homepage_links_stay_under_github_pages_project_path(self):
        homepage = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/aitoolpilot/privacy/"', homepage)
        self.assertIn('href="/aitoolpilot/affiliate-disclosure/"', homepage)
        self.assertNotIn('href="/privacy/"', homepage)
        self.assertNotIn('href="/affiliate-disclosure/"', homepage)

    def test_run_status_survives_windows_default_encoding(self):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp936"
        result = subprocess.run(
            [sys.executable, "run.py", "--status"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Environment Status", result.stdout)

    def test_auto_content_workflow_uses_deepseek_secret_name(self):
        workflow = (ROOT / ".github" / "workflows" / "auto-content.yml").read_text(encoding="utf-8")
        self.assertIn("DEEPSEEK_API_KEY", workflow)
        self.assertNotIn("ANTHROPIC_API_KEY", workflow)


if __name__ == "__main__":
    unittest.main()
