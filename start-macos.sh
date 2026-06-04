#!/usr/bin/env bash
# Ithaca — Native macOS start script
# Run this instead of Docker to get Metal GPU access for local models.
set -e

cd "$(dirname "$0")"

echo "◈ Ithaca — starting natively on macOS"
echo ""

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv .venv
fi

source .venv/bin/activate

# Install/update deps
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create data dirs
mkdir -p data data/personal_docs

# Copy .env if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Generate a random secret key
    SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
    sed -i '' "s/change-me-to-a-random-hex-string/$SECRET/" .env
    echo "Created .env with generated SECRET_KEY"
fi

echo ""
echo "Starting Ithaca on http://127.0.0.1:7860"
echo "Press Ctrl+C to stop."
echo ""

python -u -c "
import uvicorn
from app import app
uvicorn.run(app, host='127.0.0.1', port=7860)
"
