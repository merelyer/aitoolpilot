#!/bin/bash
# AI Income Automation - Setup Script
# Run once to configure everything

set -e

echo "========================================="
echo "  AI Income Automation - Setup"
echo "========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 1. Check Python
echo "[1/5] Checking Python..."
python3 --version || python --version
echo "      OK"

# 2. Install Python dependencies
echo "[2/5] Installing Python packages..."
pip install -r requirements.txt
echo "      OK"

# 3. Check for Anthropic API key
echo "[3/5] Checking Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "      WARNING: ANTHROPIC_API_KEY not set!"
    echo "      Set it with: export ANTHROPIC_API_KEY=sk-ant-..."
    echo "      Get a key at: https://console.anthropic.com/"
    echo ""
    echo "      The system will work in fallback mode without it,"
    echo "      but content quality will be lower."
else
    echo "      OK (API key found)"
fi

# 4. Create data directories
echo "[4/5] Creating data directories..."
mkdir -p data/posts data/topics data/analytics logs
echo "      OK"

# 5. Test run
echo "[5/5] Running test generation..."
python run.py --once
echo "      OK"

echo ""
echo "========================================="
echo "  ✅ Setup Complete!"
echo "========================================="
echo ""
echo "  Next steps:"
echo "  1. Set your ANTHROPIC_API_KEY"
echo "  2. Add your affiliate links in data/posts/*.json"
echo "  3. Deploy: python run.py --deploy"
echo "  4. Schedule: python run.py --schedule"
echo ""
echo "  Quick start: python run.py --once --deploy"
echo ""
