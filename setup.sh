#!/bin/bash

# Air Quality API - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "Air Quality API - Setup Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo -e "${RED}Error: Python 3.10 or higher is required${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements/development.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env file with your API keys and database settings${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create logs directory
echo ""
echo "Creating logs directory..."
mkdir -p logs
touch logs/airquality.log
echo -e "${GREEN}✓ Logs directory created${NC}"

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate
echo -e "${GREEN}✓ Migrations complete${NC}"

# Initialize default data
echo ""
echo "Initializing default data (AQI categories, data sources, etc.)..."
python manage.py init_data
echo -e "${GREEN}✓ Default data initialized${NC}"

# Create superuser prompt
echo ""
read -p "Would you like to create a superuser for Django admin? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start Redis (optional): redis-server"
echo "3. Run the development server: python manage.py runserver"
echo "4. Access the API at: http://localhost:8000/api/v1/"
echo "5. Access Django admin at: http://localhost:8000/admin/"
echo ""
echo "For more information, see README.md"
echo ""
