from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is working", "status": "ok"}

@app.get("/api/public/stats")
async def get_stats():
    return {
        "total_threats": 1234,
        "active_connections": 5,
        "threat_levels": {
            "LOW": 100,
            "MEDIUM": 200,
            "HIGH": 800,
            "CRITICAL": 134
        },
        "attack_types": {
            "Flood Attacks": 800,
            "Botnet/Mirai": 200,
            "Injection": 100,
            "Reconnaissance": 80,
            "Spoofing/MITM": 54
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/public/threats/recent")
async def get_threats():
    threats = []
    for i in range(10):
        threats.append({
            "id": f"threat-{i}",
            "timestamp": datetime.now().isoformat(),
            "source_ip": f"192.168.100.{100 + i}",
            "destination_ip": "192.168.100.124",
            "attack_type": "Flood Attacks",
            "threat_level": "HIGH",
            "confidence": 95.5,
            "description": f"Flood attack detected from source {i}",
            "blocked": False,
            "raw_data": {}
        })
    return threats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
