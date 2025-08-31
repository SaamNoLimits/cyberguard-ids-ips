#!/usr/bin/env python3
"""
Simulateur d'attaque nmap - Injecte des alertes réalistes dans la base
pour tester la détection en temps réel
"""

import psycopg2
import time
import random
from datetime import datetime, timedelta

print("🎯 SIMULATEUR ATTAQUE NMAP - INJECTION TEMPS RÉEL")
print("=" * 55)

DATABASE_URL = "postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids"

# Simulation d'une attaque nmap réaliste
NMAP_ATTACK_SEQUENCE = [
    # Phase 1: Découverte réseau
    {
        "attack_type": "Network Discovery",
        "threat_level": "LOW",
        "description": "Ping sweep - Découverte d'hôtes actifs",
        "delay": 1
    },
    {
        "attack_type": "ARP Scan",
        "threat_level": "LOW", 
        "description": "Scan ARP pour mappage réseau local",
        "delay": 2
    },
    
    # Phase 2: Scan de ports
    {
        "attack_type": "TCP SYN Scan",
        "threat_level": "MEDIUM",
        "description": "Scan SYN sur ports 1-1000 - Stealth scan",
        "delay": 3
    },
    {
        "attack_type": "Port Scan",
        "threat_level": "MEDIUM",
        "description": "Scan TCP ports 22,80,443,3389,5432",
        "delay": 2
    },
    {
        "attack_type": "UDP Scan",
        "threat_level": "MEDIUM",
        "description": "Scan UDP sur ports communs",
        "delay": 4
    },
    
    # Phase 3: Énumération de services
    {
        "attack_type": "Service Enumeration",
        "threat_level": "HIGH",
        "description": "Détection versions services (-sV)",
        "delay": 3
    },
    {
        "attack_type": "OS Fingerprinting",
        "threat_level": "HIGH",
        "description": "Identification système d'exploitation (-O)",
        "delay": 2
    },
    {
        "attack_type": "Script Scan",
        "threat_level": "HIGH",
        "description": "Exécution scripts NSE (-sC)",
        "delay": 5
    },
    
    # Phase 4: Scans avancés
    {
        "attack_type": "Aggressive Scan",
        "threat_level": "CRITICAL",
        "description": "Scan agressif avec détection vulnérabilités",
        "delay": 3
    },
    {
        "attack_type": "Vulnerability Scan",
        "threat_level": "CRITICAL",
        "description": "Scripts de détection vulnérabilités",
        "delay": 4
    }
]

def inject_attack_alert(source_ip, destination_ip, attack_info):
    """Injecte une alerte d'attaque dans la base"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO threat_alerts (
                timestamp, source_ip, destination_ip, attack_type,
                threat_level, description, blocked, confidence
            ) VALUES (
                NOW(), %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            source_ip,
            destination_ip,
            attack_info["attack_type"],
            attack_info["threat_level"],
            attack_info["description"],
            False,  # Non bloqué pour voir l'attaque
            random.uniform(0.7, 0.95)  # Score de confiance
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur injection: {e}")
        return False

def simulate_nmap_attack():
    """Simule une attaque nmap complète"""
    
    # IP source (VM Kali simulée)
    kali_ips = ["192.168.1.100", "10.0.0.50", "172.16.1.200"]
    source_ip = random.choice(kali_ips)
    
    # IP destination (machine locale)
    destination_ip = "192.168.1.10"
    
    print(f"🎯 Simulation attaque nmap:")
    print(f"   Source: {source_ip} (VM Kali)")
    print(f"   Cible: {destination_ip} (Machine locale)")
    print()
    
    print("🚀 Démarrage séquence d'attaque...")
    print("=" * 40)
    
    for i, attack_info in enumerate(NMAP_ATTACK_SEQUENCE, 1):
        print(f"📡 Phase {i}/10: {attack_info['attack_type']}")
        print(f"   Niveau: {attack_info['threat_level']}")
        print(f"   Description: {attack_info['description']}")
        
        # Injection de l'alerte
        if inject_attack_alert(source_ip, destination_ip, attack_info):
            print(f"   ✅ Alerte injectée")
        else:
            print(f"   ❌ Échec injection")
        
        # Délai réaliste entre les phases
        delay = attack_info["delay"]
        print(f"   ⏳ Attente {delay}s avant phase suivante...")
        print()
        
        time.sleep(delay)
    
    print("🎯 ATTAQUE NMAP SIMULÉE TERMINÉE!")
    print("=" * 35)
    print("✅ 10 alertes injectées en séquence")
    print("📊 Vérifiez le dashboard pour voir les détections")
    print("🔍 Consultez /threat-monitoring pour les détails")

def inject_continuous_scan():
    """Injecte un scan continu pour test prolongé"""
    source_ip = "192.168.1.100"
    destination_ip = "192.168.1.10"
    
    print("🔄 SCAN CONTINU ACTIVÉ")
    print("=" * 25)
    print("Ctrl+C pour arrêter")
    
    scan_types = [
        {"attack_type": "Port Scan", "threat_level": "MEDIUM", "description": "Scan port continu"},
        {"attack_type": "Service Probe", "threat_level": "HIGH", "description": "Sondage de services"},
        {"attack_type": "Connection Attempt", "threat_level": "LOW", "description": "Tentative de connexion"}
    ]
    
    try:
        counter = 1
        while True:
            attack_info = random.choice(scan_types)
            attack_info["description"] += f" #{counter}"
            
            if inject_attack_alert(source_ip, destination_ip, attack_info):
                print(f"📡 Alerte #{counter}: {attack_info['attack_type']}")
            
            counter += 1
            time.sleep(random.uniform(2, 8))  # Délai aléatoire
            
    except KeyboardInterrupt:
        print(f"\n🛑 Scan continu arrêté après {counter-1} alertes")

def main():
    print("🎯 OPTIONS DE SIMULATION:")
    print("=" * 30)
    print("1. 🚀 Simuler attaque nmap complète (10 phases)")
    print("2. 🔄 Scan continu (jusqu'à arrêt)")
    print("3. 📊 Injecter alerte unique de test")
    print("4. 🔍 Afficher dernières alertes")
    print("5. ❌ Quitter")
    
    while True:
        try:
            choice = input("\n👉 Votre choix (1-5): ").strip()
            
            if choice == "1":
                print("\n🎯 SIMULATION ATTAQUE NMAP COMPLÈTE")
                print("=" * 40)
                simulate_nmap_attack()
                break
                
            elif choice == "2":
                print("\n🔄 SCAN CONTINU")
                print("=" * 15)
                inject_continuous_scan()
                break
                
            elif choice == "3":
                print("\n📊 INJECTION ALERTE TEST")
                print("=" * 25)
                test_attack = {
                    "attack_type": "Test Scan",
                    "threat_level": "MEDIUM",
                    "description": f"Test injection - {datetime.now().strftime('%H:%M:%S')}"
                }
                if inject_attack_alert("192.168.1.100", "192.168.1.10", test_attack):
                    print("✅ Alerte de test injectée")
                
            elif choice == "4":
                print("\n📋 DERNIÈRES ALERTES")
                print("=" * 20)
                try:
                    conn = psycopg2.connect(DATABASE_URL)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT timestamp, source_ip, attack_type, threat_level, description
                        FROM threat_alerts 
                        ORDER BY timestamp DESC 
                        LIMIT 5
                    """)
                    alerts = cursor.fetchall()
                    
                    for alert in alerts:
                        timestamp, source_ip, attack_type, threat_level, description = alert
                        print(f"🚨 {timestamp} | {source_ip} | {attack_type} | {threat_level}")
                        print(f"   {description}")
                    
                    conn.close()
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                
            elif choice == "5":
                print("👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n👋 Arrêt du programme")
            break

if __name__ == "__main__":
    main()
