#!/usr/bin/env python3
"""
AI Income Automation - Main Runner
===================================
Fully automated Claude-powered revenue engine.

This single script orchestrates:
1. Content research & generation (via Claude API)
2. Static site building with SEO optimization
3. Deployment to free hosting (Cloudflare Pages)
4. Scheduled recurring runs

QUICK START:
    export ANTHROPIC_API_KEY=sk-ant-...
    python run.py --once          # Generate & deploy once
    python run.py --daemon        # Run continuously every N hours
    python run.py --schedule      # Set up as cron job

REVENUE MODEL:
    - Affiliate commissions from SaaS/tool recommendations
    - Ad revenue (AdSense) once traffic grows
    - Sponsored posts once domain authority builds

COST STRUCTURE:
    - Claude Haiku 3.5: ~$0.02-0.05 per post
    - Cloudflare Pages: Free tier
    - Domain (optional): ~$10/year
    - Total monthly cost with daily posts: ~$1-3

ESTIMATED REVENUE TIMELINE:
    Month 1-3: $0-50 (building content, indexing)
    Month 4-6: $50-500 (traffic growing, first affiliate conversions)
    Month 6-12: $500-2000+ (established rankings, steady traffic)
    Month 12+: $2000-10000+ (authority site with 200+ posts)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def check_environment() -> dict:
    """Check if the environment is properly set up."""
    status = {
        "python": True,
        "anthropic_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "git": False,
        "node": False,
        "wrangler": False,
        "project_dir": str(ROOT),
    }

    import shutil
    status["git"] = shutil.which("git") is not None
    status["node"] = shutil.which("node") is not None or shutil.which("npx") is not None

    return status


def print_banner():
    """Print the startup banner."""
    print(r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      █████╗ ██╗    ██╗███╗   ██╗ ██████╗ ██████╗ ███╗   ███╗███████╗
║     ██╔══██╗██║    ██║████╗  ██║██╔════╝██╔═══██╗████╗ ████║██╔════╝
║     ███████║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║██╔████╔██║█████╗
║     ██╔══██║██║███╗██║██║╚██╗██║██║     ██║   ██║██║╚██╔╝██║██╔══╝
║     ██║  ██║╚███╔███╔╝██║ ╚████║╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
║     ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝
║                                                              ║
║         🤖  Fully Automated Claude-Powered Revenue Engine  🤖║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def run_once():
    """Execute one complete cycle: generate content + build site."""
    from src.content_engine import ContentEngine

    engine = ContentEngine()
    posts = engine.run_auto()
    return posts


def run_daemon():
    """Run continuously as a daemon."""
    from src.scheduler import ContentScheduler

    scheduler = ContentScheduler()
    scheduler.run_daemon()


def deploy_site(method: str = "cloudflare"):
    """Deploy the generated site."""
    from src.deploy import DeployEngine

    deployer = DeployEngine()
    return deployer.deploy_static_host(method=method)


def setup_cron():
    """Print instructions for setting up cron/scheduled tasks."""
    script_path = ROOT / "run.py"
    python_path = sys.executable

    cron_line = f"0 */8 * * * cd {ROOT} && {python_path} {script_path} --once >> {ROOT}/logs/cron.log 2>&1"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           📅 CRON SETUP INSTRUCTIONS                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Add this line to your crontab (crontab -e):             ║
║                                                          ║
║  {cron_line}
║                                                          ║
║  This runs content generation every 8 hours.             ║
║                                                          ║
║  On Windows (Task Scheduler):                            ║
║    schtasks /create /tn "AI-Income" /tr "cmd /c cd      ║
║    {ROOT} && {python_path} {script_path} --once"  ║
║    /sc hourly /mo 8                                      ║
║                                                          ║
║  On macOS (launchd):                                     ║
║    Create ~/Library/LaunchAgents/com.ai.income.plist     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(
        description="AI Income Automation - Fully automated Claude-powered revenue engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --once          Run one content generation cycle
  python run.py --daemon        Run continuously (every N hours)
  python run.py --deploy        Deploy site to Cloudflare Pages
  python run.py --schedule      Show cron setup instructions
  python run.py --once --deploy Generate, build, AND deploy
  python run.py --status        Check environment status
        """
    )
    parser.add_argument("--once", action="store_true", help="Run one generation cycle")
    parser.add_argument("--daemon", action="store_true", help="Run as continuous daemon")
    parser.add_argument("--deploy", action="store_true", help="Deploy site after generation")
    parser.add_argument("--schedule", action="store_true", help="Show cron/scheduler setup")
    parser.add_argument("--status", action="store_true", help="Check environment status")
    parser.add_argument("--deploy-only", action="store_true", help="Deploy existing site only")
    parser.add_argument("--deploy-method", type=str, default="cloudflare",
                       choices=["cloudflare", "netlify", "github"])
    args = parser.parse_args()

    if args.status:
        print_banner()
        status = check_environment()
        print("\n📊 Environment Status:\n")
        for k, v in status.items():
            icon = "✅" if v else "❌"
            print(f"  {icon} {k}: {v}")
        print(f"\n💡 Set ANTHROPIC_API_KEY to enable Claude content generation.")
        print(f"💡 Install wrangler (npm i -g wrangler) for Cloudflare deployment.")
        return

    if args.schedule:
        setup_cron()
        return

    if args.deploy_only:
        print_banner()
        deploy_site(method=args.deploy_method)
        return

    if args.once:
        print_banner()
        status = check_environment()
        print("📊 Environment:")
        for k, v in status.items():
            print(f"  {'✅' if v else '❌'} {k}: {v}")
        print()

        posts = run_once()

        if args.deploy and posts:
            deploy_site(method=args.deploy_method)
        return

    if args.daemon:
        print_banner()
        run_daemon()
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
