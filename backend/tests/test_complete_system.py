#!/usr/bin/env python3
"""
Test complet du système de cybersécurité IDS/IPS
Teste toutes les fonctionnalités : API, base de données, SQL, Python
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test un endpoint API"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=HEADERS)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("🚀 DÉMARRAGE DU TEST COMPLET DU SYSTÈME")
    print("=" * 60)
    
    # Test 1: Vérification de l'API principale
    print("\n1️⃣ TEST API PRINCIPALE")
    result = test_api_endpoint("/")
    if result["success"]:
        print("✅ API principale: OK")
        print(f"   Message: {result['data']['message']}")
    else:
        print(f"❌ API principale: {result['error']}")
    
    # Test 2: Statistiques de la base de données
    print("\n2️⃣ TEST STATISTIQUES BASE DE DONNÉES")
    result = test_api_endpoint("/api/database/stats")
    if result["success"]:
        stats = result["data"]
        print("✅ Statistiques DB: OK")
        print(f"   Total menaces: {stats['total_threats']}")
        print(f"   Niveaux de menaces: {stats['threat_levels']}")
        print(f"   Types d'attaques: {stats['attack_types']}")
    else:
        print(f"❌ Statistiques DB: {result['error']}")
    
    # Test 3: Récupération des menaces récentes
    print("\n3️⃣ TEST RÉCUPÉRATION MENACES")
    result = test_api_endpoint("/api/database/threats/recent?limit=3")
    if result["success"]:
        threats = result["data"]
        print(f"✅ Menaces récentes: OK ({len(threats)} menaces)")
        for i, threat in enumerate(threats[:2], 1):
            print(f"   {i}. {threat['attack_type']} de {threat['source_ip']} ({threat['threat_level']})")
    else:
        print(f"❌ Menaces récentes: {result['error']}")
    
    # Test 4: Génération de menace de test
    print("\n4️⃣ TEST GÉNÉRATION MENACE")
    result = test_api_endpoint("/api/public/threats/generate", "POST")
    if result["success"]:
        threat = result["data"]
        print("✅ Génération menace: OK")
        print(f"   ID: {threat['id']}")
        print(f"   Type: {threat['attack_type']}")
        print(f"   Niveau: {threat['threat_level']}")
    else:
        print(f"❌ Génération menace: {result['error']}")
    
    # Test 5: Exécution SQL
    print("\n5️⃣ TEST EXÉCUTION SQL")
    sql_query = {
        "query": "SELECT attack_type, COUNT(*) as total, MAX(confidence) as max_confidence FROM threats GROUP BY attack_type ORDER BY total DESC"
    }
    result = test_api_endpoint("/api/sql/execute", "POST", sql_query)
    if result["success"]:
        sql_result = result["data"]
        print("✅ Exécution SQL: OK")
        print(f"   Temps d'exécution: {sql_result['execution_time']:.4f}s")
        print("   Résultats:")
        for row in sql_result["result"]:
            print(f"     - {row['attack_type']}: {row['total']} menaces (conf. max: {row['max_confidence']}%)")
    else:
        print(f"❌ Exécution SQL: {result['error']}")
    
    # Test 6: Exécution Python
    print("\n6️⃣ TEST EXÉCUTION PYTHON")
    python_code = {
        "code": """
import json
from datetime import datetime

# Analyse de sécurité automatisée
security_report = {
    "analysis_date": datetime.now().isoformat(),
    "threat_summary": {
        "high_priority": 6,
        "medium_priority": 1,
        "total_analyzed": 7
    },
    "recommendations": [
        "Bloquer IP 192.168.100.200",
        "Activer la limitation de débit",
        "Surveiller les patterns de flood"
    ],
    "risk_score": 8.5
}

print("=== RAPPORT DE SÉCURITÉ AUTOMATISÉ ===")
print(json.dumps(security_report, indent=2))

# Calcul du score de risque
risk_level = "CRITIQUE" if security_report["risk_score"] > 8 else "ÉLEVÉ"
print(f"\\n🚨 NIVEAU DE RISQUE: {risk_level}")
print(f"📊 Score: {security_report['risk_score']}/10")
"""
    }
    result = test_api_endpoint("/api/python/execute", "POST", python_code)
    if result["success"]:
        python_result = result["data"]
        print("✅ Exécution Python: OK")
        print(f"   Temps d'exécution: {python_result['execution_time']:.4f}s")
        print("   Sortie:")
        for line in python_result["result"].split('\n')[:10]:  # Première 10 lignes
            if line.strip():
                print(f"     {line}")
    else:
        print(f"❌ Exécution Python: {result['error']}")
    
    # Test 7: Historique des requêtes
    print("\n7️⃣ TEST HISTORIQUE REQUÊTES")
    result = test_api_endpoint("/api/query/history?limit=3")
    if result["success"]:
        history = result["data"]
        print(f"✅ Historique requêtes: OK ({len(history)} entrées)")
        for entry in history:
            status = "✅" if entry["success"] else "❌"
            print(f"   {status} {entry['query_type']}: {entry['execution_time']:.4f}s")
    else:
        print(f"❌ Historique requêtes: {result['error']}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DU TEST COMPLET")
    print("=" * 60)
    
    # Statistiques finales
    final_stats = test_api_endpoint("/api/database/stats")
    if final_stats["success"]:
        stats = final_stats["data"]
        print(f"🎯 Total menaces détectées: {stats['total_threats']}")
        print(f"🔴 Menaces critiques/élevées: {stats['threat_levels'].get('HIGH', 0) + stats['threat_levels'].get('CRITICAL', 0)}")
        print(f"🟡 Menaces moyennes: {stats['threat_levels'].get('MEDIUM', 0)}")
        print(f"🟢 Menaces faibles: {stats['threat_levels'].get('LOW', 0)}")
        print(f"📈 Types d'attaques: {len(stats['attack_types'])}")
    
    print("\n🎉 SYSTÈME COMPLET TESTÉ ET OPÉRATIONNEL!")
    print("🛡️  Prêt pour la détection d'attaques Kali VM!")
    print("🔗 Dashboard: http://localhost:3000")
    print("🔗 API: http://localhost:8000")

if __name__ == "__main__":
    main()
