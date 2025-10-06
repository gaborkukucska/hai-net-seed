#!/bin/bash
# START OF FILE build_ui.sh
# HAI-Net UI Build Script
# Builds the React UI and deploys it to the correct locations for the FastAPI server

set -e  # Exit on error

echo "🔨 Building HAI-Net React UI..."
echo "================================"

# Navigate to web directory
cd web

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

# Build the React app
echo "⚛️  Building React application..."
npm run build

# Deploy to static and templates directories
echo "📂 Deploying build files..."
rm -rf static/* templates/*
cp -r build/static/* static/
cp build/index.html templates/

echo "✅ UI build and deployment complete!"
echo "   Static files: web/static/"
echo "   Template: web/templates/index.html"
echo ""
echo "🚀 You can now start the server with ./launch.sh"
