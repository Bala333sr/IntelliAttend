#!/bin/bash

# IntelliAttend - Automated Setup Script
# This script sets up the entire IntelliAttend system automatically

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        info "Python version: $PYTHON_VERSION"
    else
        error "Python 3 is not installed. Please install Python 3.8 or higher."
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        info "Node.js version: $NODE_VERSION"
    else
        error "Node.js is not installed. Please install Node.js 16.0 or higher."
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        info "npm version: $NPM_VERSION"
    else
        error "npm is not installed. Please install npm."
    fi
    
    # Check Java (optional for mobile development)
    if command_exists java; then
        JAVA_VERSION=$(java -version 2>&1 | head -n 1)
        info "Java version: $JAVA_VERSION"
    else
        warn "Java is not installed. Mobile app development will not be available."
    fi
    
    log "Prerequisites check completed!"
}

# Setup backend
setup_backend() {
    log "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    log "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    log "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create environment file
    if [ ! -f ".env" ]; then
        log "Creating backend environment file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///intelliattend.db
SECRET_KEY=$(openssl rand -hex 32)

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ACCESS_TOKEN_EXPIRES=3600

# QR Code Configuration
QR_CODE_EXPIRY_MINUTES=5

# Geofencing Configuration
TILE38_HOST=localhost
TILE38_PORT=9851
EOF
    fi
    
    # Initialize database
    log "Initializing database..."
    python init_db.py
    
    # Seed database with sample data
    log "Seeding database with sample data..."
    python seed_data.py
    
    cd ..
    log "Backend setup completed!"
}

# Setup frontend
setup_frontend() {
    log "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    log "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f ".env" ]; then
        log "Creating frontend environment file..."
        cat > .env << EOF
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_WEBSOCKET_URL=ws://localhost:8765

# Development Configuration
REACT_APP_DEBUG=true
EOF
    fi
    
    cd ..
    log "Frontend setup completed!"
}

# Setup real-time presence
setup_realtime() {
    log "Setting up real-time presence service..."
    
    cd realtime_presence
    
    # Install dependencies
    log "Installing real-time service dependencies..."
    pip install -r requirements.txt
    
    cd ..
    log "Real-time service setup completed!"
}

# Setup mobile app
setup_mobile() {
    log "Setting up mobile app..."
    
    if [ ! -d "mobile/app" ]; then
        warn "Mobile app directory not found. Skipping mobile setup."
        return
    fi
    
    cd mobile/app
    
    # Make gradlew executable
    chmod +x gradlew
    
    # Check if Android SDK is available
    if command_exists android; then
        log "Android SDK found. Building mobile app..."
        ./gradlew assembleDebug
    else
        warn "Android SDK not found. Mobile app build skipped."
        info "To build the mobile app, install Android Studio and run: ./gradlew assembleDebug"
    fi
    
    cd ../..
    log "Mobile app setup completed!"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    cd database
    
    # Run database setup if script exists
    if [ -f "simple_database_setup.py" ]; then
        python3 simple_database_setup.py
    fi
    
    cd ..
    log "Database setup completed!"
}

# Create startup scripts
create_startup_scripts() {
    log "Creating startup scripts..."
    
    # Create start-all script
    cat > start-all.sh << 'EOF'
#!/bin/bash

# Start all IntelliAttend services

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log "Starting IntelliAttend services..."

# Start backend in background
log "Starting backend API server..."
cd backend
source venv/bin/activate
python run_server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
log "Starting frontend web server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Start real-time service in background
log "Starting real-time presence service..."
cd realtime_presence
python server.py &
REALTIME_PID=$!
cd ..

info "All services started!"
info "Backend API: http://localhost:8080"
info "Frontend Web: http://localhost:3000"
info "WebSocket: ws://localhost:8765"
info ""
info "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    log "Stopping all services..."
    kill $BACKEND_PID $FRONTEND_PID $REALTIME_PID 2>/dev/null
    log "All services stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait
EOF
    
    chmod +x start-all.sh
    
    # Create stop-all script
    cat > stop-all.sh << 'EOF'
#!/bin/bash

# Stop all IntelliAttend services

echo "Stopping IntelliAttend services..."

# Kill processes by port
pkill -f "run_server.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "server.py" 2>/dev/null || true

# Kill by common process names
pkill -f "python.*run_server" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true
pkill -f "python.*server.py" 2>/dev/null || true

echo "All services stopped."
EOF
    
    chmod +x stop-all.sh
    
    log "Startup scripts created!"
}

# Create development guide
create_dev_guide() {
    log "Creating development guide..."
    
    cat > DEVELOPMENT.md << 'EOF'
# Development Guide

## Quick Start

After running the setup script, you can start development immediately:

```bash
# Start all services
./start-all.sh

# Or start services individually:

# Backend only
cd backend && source venv/bin/activate && python run_server.py

# Frontend only
cd frontend && npm start

# Real-time service only
cd realtime_presence && python server.py
```

## Service URLs

- **Backend API**: http://localhost:8080
- **Frontend Web**: http://localhost:3000
- **WebSocket**: ws://localhost:8765
- **API Documentation**: http://localhost:8080/docs

## Development Workflow

1. **Backend Development**: Edit Python files in `backend/`, server auto-reloads
2. **Frontend Development**: Edit React files in `frontend/src/`, hot reload enabled
3. **Mobile Development**: Open `mobile/app/` in Android Studio

## Testing

```bash
# Test backend API
curl http://localhost:8080/health

# Test frontend
open http://localhost:3000

# Build mobile app
cd mobile/app && ./gradlew assembleDebug
```

## Database Management

```bash
# Reset database
cd backend && python reset_db.py

# Add sample data
python seed_data.py

# Check tables
python show_tables.py
```

## Troubleshooting

- **Port conflicts**: Update ports in respective config files
- **Dependencies**: Run setup script again
- **Database issues**: Delete `backend/intelliattend.db` and run `python init_db.py`
EOF
    
    log "Development guide created!"
}

# Main setup function
main() {
    log "Starting IntelliAttend automated setup..."
    
    # Get current directory
    SETUP_DIR=$(pwd)
    
    # Check prerequisites
    check_prerequisites
    
    # Setup components
    setup_backend
    setup_frontend
    setup_realtime
    setup_database
    setup_mobile
    
    # Create utility scripts
    create_startup_scripts
    create_dev_guide
    
    log "Setup completed successfully!"
    info ""
    info "🎉 IntelliAttend is ready to use!"
    info ""
    info "Quick start:"
    info "  ./start-all.sh    # Start all services"
    info "  ./stop-all.sh     # Stop all services"
    info ""
    info "Service URLs:"
    info "  Backend API:  http://localhost:8080"
    info "  Frontend Web: http://localhost:3000"
    info "  WebSocket:    ws://localhost:8765"
    info ""
    info "For detailed instructions, see SETUP.md and DEVELOPMENT.md"
    info ""
    info "To start development now, run: ./start-all.sh"
}

# Run main function
main "$@"