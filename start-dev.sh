#!/bin/bash
# =============================================================================
# Brand Analytics - Local Development Startup Script
# =============================================================================
# This script helps you start the application for local development.
#
# Usage:
#   ./start-dev.sh          # Start everything with Docker
#   ./start-dev.sh docker   # Start only Docker services (Postgres, Redis)
#   ./start-dev.sh backend  # Start backend only (requires Docker services)
#   ./start-dev.sh frontend # Start frontend only
#   ./start-dev.sh all      # Start all services locally (no Docker)
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Brand Analytics Development Startup${NC}"
echo ""

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
    return 0
}

# Function to check if Docker is running
check_docker() {
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
        exit 1
    fi
}

# Function to start Docker services (Postgres + Redis)
start_docker_services() {
    echo -e "${YELLOW}📦 Starting Docker services (Postgres + Redis)...${NC}"
    docker-compose up -d postgres redis
    echo -e "${GREEN}✅ Database and Redis are running${NC}"
    echo ""
}

# Function to start backend
start_backend() {
    echo -e "${YELLOW}🐍 Starting Backend...${NC}"
    cd backend
    
    # Check for virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/.installed" ]; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
        touch venv/.installed
    fi
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Copying from env.example...${NC}"
        cp env.example .env
        echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys!${NC}"
    fi
    
    echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
    uvicorn app.main:app --reload --port 8000
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}⚛️  Starting Frontend...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing Node dependencies...${NC}"
        npm install
    fi
    
    # Check for .env.local
    if [ ! -f ".env.local" ]; then
        echo -e "${YELLOW}Creating .env.local with default API URL...${NC}"
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
    
    echo -e "${GREEN}Starting Next.js dev server on http://localhost:3000${NC}"
    npm run dev
}

# Parse command
MODE=${1:-"docker"}

case $MODE in
    "docker")
        echo -e "${GREEN}Starting full stack with Docker...${NC}"
        check_docker
        
        # Check for root .env
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}⚠️  No .env file found. Copying from .env.example...${NC}"
            cp .env.example .env
            echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
            echo ""
        fi
        
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✅ All services started!${NC}"
        echo ""
        echo "📍 Frontend:      http://localhost:3000"
        echo "📍 Backend API:   http://localhost:8000"
        echo "📍 API Docs:      http://localhost:8000/docs"
        echo "📍 Flower:        http://localhost:5555"
        echo ""
        echo "📝 View logs:     docker-compose logs -f"
        echo "🛑 Stop:          docker-compose down"
        ;;
        
    "services")
        check_docker
        start_docker_services
        ;;
        
    "backend")
        check_command python3
        start_backend
        ;;
        
    "frontend")
        check_command node
        start_frontend
        ;;
        
    "all")
        echo -e "${YELLOW}Starting all services locally...${NC}"
        echo "This will start Postgres and Redis with Docker, then run backend and frontend locally."
        echo ""
        
        check_docker
        check_command python3
        check_command node
        
        start_docker_services
        
        # Start backend in background
        echo -e "${YELLOW}Starting backend in background...${NC}"
        (cd backend && source venv/bin/activate 2>/dev/null || true && uvicorn app.main:app --reload --port 8000) &
        BACKEND_PID=$!
        
        sleep 3
        
        # Start frontend
        start_frontend
        
        # Cleanup on exit
        trap "kill $BACKEND_PID 2>/dev/null" EXIT
        ;;
        
    *)
        echo "Usage: $0 [docker|services|backend|frontend|all]"
        echo ""
        echo "  docker    - Start everything with Docker (default)"
        echo "  services  - Start only Postgres + Redis in Docker"
        echo "  backend   - Start Python backend locally"
        echo "  frontend  - Start Next.js frontend locally"
        echo "  all       - Start DB in Docker, backend + frontend locally"
        exit 1
        ;;
esac
