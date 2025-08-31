#!/bin/bash

# Cybersecurity IDS/IPS Platform with Real Network Capture
echo "🔒 Starting Cybersecurity IDS/IPS Platform with Network Capture..."
echo "=================================================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root for network packet capture!"
    echo "   Please run: sudo ./start_with_network_capture.sh"
    exit 1
fi

echo "✅ Running as root - full network monitoring enabled"

# Show available network interfaces
echo "🌐 Available Network Interfaces:"
ip addr show | grep -E "^[0-9]+:" | sed 's/^/   /'

echo ""
echo "🎯 Detected VM Networks:"
ip addr show | grep -E "(vmnet|192\.168\.(162|11))" | sed 's/^/   /'

echo ""
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
NETWORK_INTERFACE=auto
CAPTURE_FILTER=
EOF

# Frontend .env
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
EOF

echo "✅ Environment files created"

# Start backend with root privileges
echo "🚀 Starting Backend API with Network Capture..."
cd backend/backend

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# Start FastAPI server with root privileges for packet capture
echo "🌐 Starting FastAPI server with network capture on http://localhost:8000"
echo "🔍 Monitoring interfaces: wlp0s20f3, vmnet1, vmnet8"
echo "🎯 Ready to detect attacks from Kali VM!"
echo ""
echo "📊 Dashboard will be available at: http://localhost:3000/threat-monitoring"
echo "🔗 API Documentation: http://localhost:8000/docs"
echo ""
echo "🚨 ATTACK DETECTION ACTIVE - Launch attacks from your Kali VM!"
echo "   Supported attacks: nmap, nikto, sqlmap, metasploit, etc."
echo ""

# Start the backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo $BACKEND_PID > ../../.backend_pid

# Wait a moment for backend to start
sleep 5

# Start frontend in background
echo "🎨 Starting Frontend Dashboard..."
cd ../../cybersecurity-dashboard

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install --silent
fi

echo "🌐 Starting Next.js development server on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend_pid

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8000"
    echo "   📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend API failed to start"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend Dashboard is running at http://localhost:3000"
else
    echo "❌ Frontend Dashboard failed to start"
fi

echo ""
echo "🎉 Platform Started Successfully with Network Capture!"
echo "======================================================"
echo ""
echo "🌐 Access Points:"
echo "   • Main Dashboard:    http://localhost:3000"
echo "   • Threat Monitoring: http://localhost:3000/threat-monitoring"
echo "   • API Backend:       http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🔐 Network Monitoring:"
echo "   • Interface: wlp0s20f3 (192.168.100.124)"
echo "   • VM Networks: vmnet1 (192.168.162.x), vmnet8 (192.168.11.x)"
echo "   • Packet Capture: ENABLED"
echo "   • ML Detection: ACTIVE"
echo ""
echo "🎯 Kali VM Attack Instructions:"
echo "   1. Ensure your Kali VM can reach 192.168.100.124"
echo "   2. Launch attacks against this IP or scan the network"
echo "   3. Watch real-time detection in the dashboard"
echo ""
echo "📋 Example Kali Commands:"
echo "   • nmap -sS -O 192.168.100.124"
echo "   • nmap -sV -p- 192.168.100.124"
echo "   • nikto -h http://192.168.100.124:3000"
echo "   • sqlmap -u 'http://192.168.100.124:8000/api/test?id=1'"
echo ""
echo "🛑 To stop the platform:"
echo "   Press Ctrl+C or run: ./stop_platform.sh"
echo ""
echo "Press Ctrl+C to stop the platform..."

# Wait for user interrupt
trap 'echo -e "\n🛑 Stopping platform..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Keep script running
while true; do
    sleep 1
done
