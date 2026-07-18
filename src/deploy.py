#!/usr/bin/env python3
"""
AI Income Automation - Deployment Engine
Handles deployment to Cloudflare Pages, Netlify, or GitHub Pages.
Fully automated deployment pipeline.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent


class DeployEngine:
    """Automated deployment to multiple platforms."""

    def __init__(self):
        self.site_dir = ROOT / "site"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        config_path = ROOT / "config" / "settings.json"
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def deploy_cloudflare_pages(self, project_name: str = "aitoolpilot") -> bool:
        """Deploy to Cloudflare Pages using Wrangler CLI."""
        print("\n☁️  Deploying to Cloudflare Pages...")

        # Check if wrangler is installed
        if not shutil.which("wrangler") and not shutil.which("npx"):
            print("[WARN] Cloudflare Wrangler not installed.")
            print("       Install: npm install -g wrangler")
            print("       Then: wrangler login")
            return False

        # Create wrangler.toml if not exists
        wrangler_config = f"""name = "{project_name}"
compatibility_date = "2025-07-18"
pages_build_output_dir = "site"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
        with open(ROOT / "wrangler.toml", "w") as f:
            f.write(wrangler_config)

        try:
            cmd = ["npx", "wrangler", "pages", "deploy", str(self.site_dir), "--project-name", project_name]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
            if result.returncode == 0:
                print(f"✅ Deployed to Cloudflare Pages: {project_name}.pages.dev")
                return True
            else:
                print(f"[ERROR] Deployment failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Deployment error: {e}")
            return False

    def deploy_netlify(self) -> bool:
        """Deploy to Netlify using their CLI."""
        print("\n🚀 Deploying to Netlify...")

        if not shutil.which("netlify"):
            print("[WARN] Netlify CLI not installed.")
            print("       Install: npm install -g netlify-cli")
            return False

        try:
            result = subprocess.run(
                ["netlify", "deploy", "--dir", str(self.site_dir), "--prod"],
                capture_output=True, text=True,
                cwd=str(ROOT)
            )
            if result.returncode == 0:
                print(f"✅ Deployed to Netlify")
                return True
            else:
                print(f"[ERROR] Netlify deploy failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def deploy_github_pages(self) -> bool:
        """Deploy to GitHub Pages."""
        print("\n🐙 Deploying to GitHub Pages...")
        print("[INFO] To deploy to GitHub Pages:")
        print("       1. Create a GitHub repo")
        print("       2. Push the 'site/' directory to gh-pages branch")
        print("       3. Or set GitHub Pages to serve from main branch /docs folder")

        # Copy site to docs folder (GitHub Pages convention)
        docs_dir = ROOT / "docs"
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        shutil.copytree(self.site_dir, docs_dir)
        print(f"✅ Site copied to {docs_dir}/ for GitHub Pages deployment")
        return True

    def deploy_static_host(self, method: str = "cloudflare") -> bool:
        """Main deployment dispatcher."""
        methods = {
            "cloudflare": self.deploy_cloudflare_pages,
            "netlify": self.deploy_netlify,
            "github": self.deploy_github_pages,
        }

        if method not in methods:
            print(f"[ERROR] Unknown deployment method: {method}")
            print(f"       Available: {list(methods.keys())}")
            return False

        return methods[method]()

    def verify_deployment(self, url: str = None) -> bool:
        """Verify the site is live and working."""
        print(f"\n🔍 Verifying deployment...")
        if url:
            try:
                import urllib.request
                response = urllib.request.urlopen(url)
                if response.status == 200:
                    print(f"✅ Site is live at {url}")
                    return True
            except Exception as e:
                print(f"[ERROR] Verification failed: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Income Automation - Deploy Engine")
    parser.add_argument("--method", type=str, default="cloudflare",
                       choices=["cloudflare", "netlify", "github"],
                       help="Deployment target")
    parser.add_argument("--verify", type=str, default=None,
                       help="URL to verify after deployment")
    args = parser.parse_args()

    engine = DeployEngine()
    success = engine.deploy_static_host(method=args.method)

    if success and args.verify:
        engine.verify_deployment(args.verify)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
