#!/bin/bash

# atlas_core07 Setup Script
# Complete installation and configuration

echo "======================================"
echo "atlas_core07 - AI Chatbot Platform"
echo "Setup & Installation"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check Node
echo -e "${BLUE}[2/5] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js 16+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"

# Setup Backend
echo ""
echo -e "${BLUE}[3/5] Setting up Backend...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Backend configured${NC}"

# Create .env
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || echo "AI_PROVIDER=mock" > .env
    echo -e "${GREEN}✓ Backend .env created${NC}"
fi

cd ..

# Setup Frontend
echo ""
echo -e "${BLUE}[4/5] Setting up Frontend...${NC}"
cd frontend
npm install > /dev/null 2>&1
echo -e "${GREEN}✓ Frontend configured${NC}"

# Create .env
if [ ! -f .env ]; then
    echo "VITE_API_URL=http://localhost:5000/api" > .env
    echo -e "${GREEN}✓ Frontend .env created${NC}"
fi

cd ..

# Create directories
echo ""
echo -e "${BLUE}[5/5] Creating directories...${NC}"
mkdir -p backend/logs
mkdir -p backend/tests
echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo "======================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "Terminal 1 - Start Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 - Start Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "For configuration options, see README.md"
echo ""
