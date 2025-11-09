#!/bin/bash
# Quick setup script for Jira MCP server

set -e

echo "Setting up Jira MCP Server..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed"
    exit 1
fi

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Check for .env
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "JIRA_URL=your_jira_url_here" > .env
    echo "JIRA_EMAIL=your_email_here" >> .env
    echo "JIRA_API_TOKEN=your_api_token_here" >> .env
    echo "Please update .env with your Jira credentials"
    echo "Get API token from: https://id.atlassian.com/manage-profile/security/api-tokens"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Jira URL, email, and API token"
echo "2. Add MCP config to Cursor (see mcp.json.example)"
echo "3. Restart Cursor"
echo "4. Test: Ask Cursor to list projects from Jira"

