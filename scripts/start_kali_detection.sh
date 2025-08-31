#!/bin/bash

echo "🎯 Starting Cybersecurity IDS/IPS Platform for Kali Attack Detection"
echo "===================================================================="

# Kill any existing processes
echo "🛑 Stopping existing processes..."
pkill -f "uvicorn\|node\|npm" || true
sleep 2

echo "🚀 Starting Backend API (Normal Mode)..."
cd backend/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo $BACKEND_PID > ../../.backend_pid

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 8

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend Dashboard..."
cd ../../frontend
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend_pid

# Wait for frontend
echo "⏳ Waiting for frontend to start..."
sleep 5

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend Dashboard is running at http://localhost:3000"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 Platform Started Successfully!"
echo "================================="
echo ""
echo "🌐 Access Points:"
echo "   • Main Dashboard:    http://localhost:3000"
echo "   • Threat Monitoring: http://localhost:3000/threat-monitoring"
echo "   • API Backend:       http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🔍 Current Status:"
echo "   • Network Monitoring: Sample mode (no root privileges)"
echo "   • ML Detection: Active"
echo "   • Kali Signature Detection: Active"
echo "   • Real-time Alerts: Enabled"
echo ""
echo "🎯 Kali VM Attack Instructions:"
echo "   1. Ensure your Kali VM can reach 192.168.100.124"
echo "   2. Launch attacks against this IP:"
echo "      • nmap -sS -O 192.168.100.124"
echo "      • nmap -sV -p- 192.168.100.124"
echo "      • nikto -h http://192.168.100.124:3000"
echo "      • sqlmap -u 'http://192.168.100.124:8000/api/public/threats/recent?id=1'"
echo "   3. Watch real-time detection in the dashboard"
echo ""
echo "🔐 For Real Network Capture (Optional):"
echo "   Run: sudo ./start_with_network_capture.sh"
echo "   This enables actual packet capture from network interfaces"
echo ""
echo "🧪 Test Attack Simulation:"
echo "   Run: python3 test_kali_detection.py"
echo ""
echo "📊 Generate Sample Threats:"
echo "   curl -X POST http://localhost:8000/api/public/threats/generate"
echo ""
echo "🛑 To stop the platform:"
echo "   Press Ctrl+C or run: ./stop_platform.sh"
echo ""
echo "Platform is ready! Monitor attacks at: http://localhost:3000/threat-monitoring"

# Keep script running
trap 'echo -e "\n🛑 Stopping platform..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

echo "Press Ctrl+C to stop the platform..."
while true; do
    sleep 1
done
