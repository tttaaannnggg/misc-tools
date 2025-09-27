#!/bin/bash

# Zoom Scheduler Setup Script
# This script helps new users set up the environment safely

echo "🚀 Setting up Zoom Meeting Scheduler..."

# Check if we're in the right directory
if [ ! -f "tool/zoom_scheduler.py" ]; then
    echo "❌ Error: Please run this script from the zoom_scheduler/ directory"
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
cd tool/
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Go back to root directory
cd ..

# Copy configuration template
echo "⚙️  Setting up configuration..."
if [ ! -f "configs/zoom_config.json" ]; then
    echo "📝 Copying configuration template..."
    cp configs/zoom_config_multi.json.sample configs/zoom_config.json
    echo "✅ Configuration template created at configs/zoom_config.json"
    echo "❗ IMPORTANT: Edit this file with your Zoom API credentials"
else
    echo "ℹ️  Configuration file already exists at configs/zoom_config.json"
fi

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Copying environment template..."
    cp .env.example .env
    echo "✅ Environment template created at .env"
    echo "❗ IMPORTANT: Edit this file with your environment variables"
else
    echo "ℹ️  Environment file already exists at .env"
fi

# Create results directory if it doesn't exist
mkdir -p results

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit configs/zoom_config.json with your Zoom API credentials"
echo "2. Test with: cd tool && python3 zoom_scheduler.py ../events/events_sample.json --dry-run"
echo "3. See USAGE_EXAMPLES.md for more examples"
echo ""
echo "🔒 Security reminder:"
echo "- Never commit configs/zoom_config.json to git"
echo "- Never commit .env file to git"
echo "- These files are automatically excluded by .gitignore"
echo ""
echo "📚 Documentation:"
echo "- README.md - Main documentation"
echo "- SECURITY.md - Security guidelines"
echo "- USAGE_EXAMPLES.md - Usage examples"