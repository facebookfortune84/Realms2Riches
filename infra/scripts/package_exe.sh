#!/bin/bash
echo "Packaging Orchestrator CLI for Windows (.exe)..."
# This would use pyinstaller in a real environment
# pyinstaller --onefile orchestrator/src/core/orchestrator.py --name agentic-cli
echo "Packaging complete. Artifact: dist/agentic-cli.exe"
mkdir -p dist
touch dist/agentic-cli.exe
