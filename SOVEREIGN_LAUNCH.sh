#!/bin/bash
# ============================================================
# SOVEREIGN_LAUNCH.sh - Linux/VPS Deployment Script
# ============================================================

ENV_FILE=".env.prod"
if [ "$1" == "--local" ]; then
    ENV_FILE=".env"
fi

echo "🚀 Launching Realms2Riches Sovereign Stack ($ENV_FILE)..."

# 1. Pull Latest Changes
echo "📡 Pulling latest updates from GitHub..."
git pull origin clickfunnels-ignition

# 2. Environment Verification
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ ERROR: $ENV_FILE not found. Initialization failed."
    exit 1
fi

# 3. Docker Orchestration
echo "🐳 Building/Starting Docker Containers..."
docker-compose -f infra/docker/docker-compose.yml --env-file "$ENV_FILE" down --remove-orphans
docker-compose -f infra/docker/docker-compose.yml --env-file "$ENV_FILE" up -d --build

# 4. Connectivity Verification
echo "📡 Verifying Backend Connectivity..."
sleep 5
HEALTH=$(curl -s http://localhost:8000/health)
if [[ $HEALTH == *"ok"* ]]; then
    echo "✅ Backend is ONLINE."
else
    echo "⚠️  Backend check failed. Check logs: docker-compose logs orchestrator"
fi

echo "🏆 SYSTEM IS LIVE. MISSION: LAMBORGHINI RUN."
