#!/bin/bash

# CyberGuard IDS/IPS Platform Setup Script
# This script sets up the complete cybersecurity platform

set -e

echo "🛡️  CyberGuard IDS/IPS Platform Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for network monitoring
check_privileges() {
    print_status "Checking system privileges..."
    if [[ $EUID -eq 0 ]]; then
        print_success "Running as root - network monitoring enabled"
        NETWORK_MONITORING=true
    else
        print_warning "Not running as root - network monitoring will be limited"
        print_warning "For full functionality, run: sudo ./setup.sh"
        NETWORK_MONITORING=false
    fi
}

# Check system dependencies
check_dependencies() {
    print_status "Checking system dependencies..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client found"
    else
        print_warning "PostgreSQL client not found. Database features may be limited."
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found. Using local services only."
        DOCKER_AVAILABLE=false
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install fastapi uvicorn sqlalchemy psycopg2-binary redis websockets
    pip install pandas numpy matplotlib seaborn lightgbm scapy
    pip install python-multipart jinja2 python-jose[cryptography]
    
    # Setup environment file
    if [ ! -f "backend/.env" ]; then
        print_status "Creating environment configuration..."
        cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# ML Model Configuration
ML_MODEL_PATH=../ml-iot/iot_ids_lightgbm_20250819_132715.pkl

# Network Configuration
NETWORK_INTERFACE=auto
TARGET_IP=192.168.100.124

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cybersec.log
EOF
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    else
        print_status "Updating Node.js dependencies..."
        npm update
    fi
    
    # Create environment file
    if [ ! -f ".env.local" ]; then
        print_status "Creating frontend environment configuration..."
        cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Application Configuration
NEXT_PUBLIC_APP_NAME=CyberGuard IDS/IPS
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_status "Starting PostgreSQL and Redis with Docker..."
        cd backend
        docker-compose up -d postgres redis
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        
        # Create database schema
        print_status "Creating database schema..."
        docker-compose exec postgres psql -U cybersec -d cybersec_ids -f /docker-entrypoint-initdb.d/create_reports_tables.sql || true
        
        cd ..
    else
        print_warning "Docker not available. Please setup PostgreSQL and Redis manually."
        print_warning "Database URL: postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids"
        print_warning "Redis URL: redis://localhost:6379"
    fi
    
    print_success "Database setup completed"
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting CyberGuard IDS/IPS Platform..."

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python backend/main.py &
BACKEND_PID=$!
echo $BACKEND_PID > ../.backend_pid
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend_pid
cd ..

echo "✅ Platform started successfully!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the platform, run: ./stop.sh"
EOF

    chmod +x start.sh
    
    # Create stop script
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping CyberGuard IDS/IPS Platform..."

# Stop backend
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm .backend_pid
    echo "Backend stopped"
fi

# Stop frontend
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm .frontend_pid
    echo "Frontend stopped"
fi

echo "✅ Platform stopped successfully!"
EOF

    chmod +x stop.sh
    
    print_success "Startup scripts created"
}

# Main setup function
main() {
    echo ""
    print_status "Starting CyberGuard IDS/IPS Platform setup..."
    echo ""
    
    check_privileges
    check_dependencies
    setup_backend
    setup_frontend
    setup_database
    create_startup_script
    
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Start the platform: ./start.sh"
    echo "2. Open dashboard: http://localhost:3000"
    echo "3. Check API docs: http://localhost:8000/docs"
    echo "4. Run tests: ./scripts/quick_test_all.sh"
    echo ""
    echo "📚 Documentation:"
    echo "- Project structure: ./PROJECT_STRUCTURE.md"
    echo "- Platform scripts: ./docs/PLATFORM_SCRIPTS.md"
    echo "- Main README: ./README.md"
    echo ""
    
    if [ "$NETWORK_MONITORING" = false ]; then
        print_warning "⚠️  For full network monitoring capabilities, run setup as root:"
        print_warning "   sudo ./setup.sh"
    fi
}

# Run main function
main "$@"
