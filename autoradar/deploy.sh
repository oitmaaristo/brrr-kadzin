#!/bin/bash
# Autoradar deploy script for VPS
# Usage: ./deploy.sh

set -e

DEPLOY_DIR="/home/brrr/brrr-autoradar"
REPO_URL="https://github.com/oitmaaristo/brrr-kadzin.git"
BRANCH="claude/car-listing-notifications-XvvUU"

echo "=== Autoradar Deploy ==="

# Create deploy directory
mkdir -p "$DEPLOY_DIR"

# Clone or pull
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "Pulling latest changes..."
    cd "$DEPLOY_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo "Cloning repo..."
    git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# Move to autoradar directory
cd "$DEPLOY_DIR/autoradar"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env to add your Telegram bot token and chat ID:"
    echo "  nano $DEPLOY_DIR/autoradar/.env"
    echo ""
fi

# Build and start
echo "Building Docker containers..."
docker compose build

echo "Starting services..."
docker compose up -d

echo ""
echo "=== Deploy Complete ==="
echo ""
echo "Services:"
echo "  Backend API:  http://localhost:8000/api/health"
echo "  Frontend UI:  http://$(hostname -I | awk '{print $1}'):3001"
echo "  Database:     localhost:5432"
echo ""
echo "Commands:"
echo "  Logs:         cd $DEPLOY_DIR/autoradar && docker compose logs -f"
echo "  Stop:         cd $DEPLOY_DIR/autoradar && docker compose down"
echo "  Restart:      cd $DEPLOY_DIR/autoradar && docker compose restart"
echo ""
echo "Next steps:"
echo "  1. Edit .env: nano $DEPLOY_DIR/autoradar/.env"
echo "  2. Add Telegram bot token and chat ID"
echo "  3. Restart: docker compose restart backend"
