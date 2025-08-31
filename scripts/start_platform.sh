#!/bin/bash

# Cybersecurity IDS/IPS Platform Startup Script
echo "🔒 Starting Cybersecurity IDS/IPS Platform..."
echo "=============================================="

# Check if running as root (needed for network monitoring)
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running as root - full network monitoring enabled"
else
    echo "⚠️  Not running as root - limited network monitoring"
    echo "   For full functionality, run: sudo ./start_platform.sh"
fi

# Create environment files
echo "📝 Setting up environment..."

# Backend .env
mkdir -p backend/backend
cat > backend/backend/.env << 'EOF'
DATABASE_URL=postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=cybersec-super-secret-key-change-in-production
ML_MODEL_PATH=../ml-iot/iot_ids_lightgbm_20250819_132715.pkl
DEBUG=true
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
EOF

# Frontend .env
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
EOF

echo "✅ Environment files created"

# Start backend
echo "🚀 Starting Backend API..."
cd backend/backend

# Install Python dependencies
if command -v python3 &> /dev/null; then
    echo "📦 Installing Python dependencies..."
    python3 -m pip install -r requirements.txt --quiet
    
    # Start FastAPI server
    echo "🌐 Starting FastAPI server on http://localhost:8000"
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
else
    echo "❌ Python3 not found. Please install Python 3.11+"
    exit 1
fi

cd ../../

# Start frontend
echo "🎨 Starting Frontend Dashboard..."
cd frontend

if command -v npm &> /dev/null; then
    echo "📦 Installing Node.js dependencies..."
    npm install --silent
    
    echo "🌐 Starting Next.js development server on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
elif command -v pnpm &> /dev/null; then
    echo "📦 Installing Node.js dependencies with pnpm..."
    pnpm install --silent
    
    echo "🌐 Starting Next.js development server on http://localhost:3000"
    pnpm dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
else
    echo "❌ Node.js/npm not found. Please install Node.js 18+"
    exit 1
fi

cd ..

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
echo "🔍 Checking service status..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:8000"
    echo "   📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend API failed to start"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend Dashboard is running at http://localhost:3000"
else
    echo "⏳ Frontend is still starting..."
fi

echo ""
echo "🎉 Platform Started Successfully!"
echo "=================================="
echo ""
echo "🌐 Access Points:"
echo "   • Main Dashboard:    http://localhost:3000"
echo "   • API Backend:       http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🔐 Default Login:"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "📊 Features Available:"
echo "   • Real-time threat monitoring"
echo "   • IoT attack detection (LightGBM ML model)"
echo "   • Network traffic analysis"
echo "   • Blockchain audit trail"
echo "   • WebSocket live updates"
echo ""
echo "🛑 To stop the platform:"
echo "   Press Ctrl+C or run: ./stop_platform.sh"
echo ""

# Save PIDs for cleanup
echo "Backend PID: $BACKEND_PID saved to .backend_pid"
echo $BACKEND_PID > .backend_pid
echo "Frontend PID: $FRONTEND_PID saved to .frontend_pid"
echo $FRONTEND_PID > .frontend_pid

# Keep script running
trap 'echo ""; echo "🛑 Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend_pid .frontend_pid; exit' INT

echo "Press Ctrl+C to stop the platform..."
wait
