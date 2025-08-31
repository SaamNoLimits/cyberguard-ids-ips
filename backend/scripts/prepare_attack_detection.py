#!/usr/bin/env python3
"""
Script pour préparer la détection d'attaque nmap en temps réel
Active le monitoring réseau et prépare les alertes
"""

import asyncio
import psycopg2
import subprocess
import socket
import time
from datetime import datetime
import threading
import sys
import os

print("🛡️ PRÉPARATION DÉTECTION ATTAQUE NMAP")
print("=" * 50)

# Configuration
DATABASE_URL = "postgresql://cybersec:secure_password_123@localhost:5432/cybersec_ids"

def get_local_ip():
    """Obtient l'IP locale de la machine"""
    try:
        # Connexion à un serveur externe pour déterminer l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def setup_database():
    """Prépare la base de données pour les nouvelles alertes"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Marquer le début de la session de test
        cursor.execute("""
            INSERT INTO threat_alerts (
                timestamp, source_ip, destination_ip, attack_type, 
                threat_level, description, blocked, confidence_score
            ) VALUES (
                NOW(), 'SYSTEM', %s, 'TEST_SESSION_START', 
                'INFO', 'Début session test détection nmap', false, 1.0
            )
        """, (get_local_ip(),))
        
        conn.commit()
        conn.close()
        print("✅ Base de données préparée pour détection")
        return True
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def start_network_monitoring():
    """Active le monitoring réseau avec tcpdump"""
    local_ip = get_local_ip()
    print(f"🌐 IP locale détectée: {local_ip}")
    
    # Commande tcpdump pour détecter les scans nmap
    tcpdump_cmd = [
        "sudo", "tcpdump", "-i", "any", "-n", "-q",
        f"host {local_ip} and (tcp[tcpflags] & tcp-syn != 0)",
        "-c", "100"  # Limite à 100 paquets pour le test
    ]
    
    print("🔍 Démarrage monitoring réseau...")
    print(f"📡 Commande: {' '.join(tcpdump_cmd)}")
    print("⚠️  Assurez-vous d'avoir les droits sudo pour tcpdump")
    
    return tcpdump_cmd, local_ip

def monitor_new_threats():
    """Surveille les nouvelles menaces dans la base"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Compte initial
        cursor.execute("SELECT COUNT(*) FROM threat_alerts WHERE timestamp >= NOW() - INTERVAL '5 minutes'")
        initial_count = cursor.fetchone()[0]
        
        print(f"📊 Alertes actuelles (5 min): {initial_count}")
        
        # Monitoring en continu
        print("👁️  Surveillance active des nouvelles menaces...")
        print("   (Ctrl+C pour arrêter)")
        
        last_count = initial_count
        while True:
            time.sleep(2)
            
            cursor.execute("""
                SELECT COUNT(*), MAX(timestamp) 
                FROM threat_alerts 
                WHERE timestamp >= NOW() - INTERVAL '5 minutes'
            """)
            current_count, last_alert = cursor.fetchone()
            
            if current_count > last_count:
                new_alerts = current_count - last_count
                print(f"🚨 NOUVELLE(S) ALERTE(S) DÉTECTÉE(S): +{new_alerts}")
                print(f"⏰ Dernière alerte: {last_alert}")
                
                # Afficher les dernières alertes
                cursor.execute("""
                    SELECT timestamp, source_ip, attack_type, threat_level, description
                    FROM threat_alerts 
                    WHERE timestamp >= NOW() - INTERVAL '30 seconds'
                    ORDER BY timestamp DESC
                    LIMIT 3
                """)
                
                recent_alerts = cursor.fetchall()
                for alert in recent_alerts:
                    timestamp, source_ip, attack_type, threat_level, description = alert
                    print(f"   📍 {timestamp} | {source_ip} | {attack_type} | {threat_level}")
                    print(f"      {description}")
                
                last_count = current_count
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du monitoring")
    except Exception as e:
        print(f"❌ Erreur monitoring: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def create_test_alerts():
    """Crée quelques alertes de test pour simuler la détection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        test_alerts = [
            ("192.168.1.100", "Port Scan", "MEDIUM", "Scan de ports détecté"),
            ("192.168.1.100", "Service Enumeration", "MEDIUM", "Énumération de services"),
            ("192.168.1.100", "OS Fingerprinting", "LOW", "Tentative d'identification OS"),
        ]
        
        for source_ip, attack_type, threat_level, description in test_alerts:
            cursor.execute("""
                INSERT INTO threat_alerts (
                    timestamp, source_ip, destination_ip, attack_type, 
                    threat_level, description, blocked, confidence_score
                ) VALUES (
                    NOW(), %s, %s, %s, %s, %s, false, 0.8
                )
            """, (source_ip, get_local_ip(), attack_type, threat_level, description))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(test_alerts)} alertes de test créées")
        
    except Exception as e:
        print(f"❌ Erreur création alertes test: {e}")

def main():
    print("🎯 INSTRUCTIONS POUR ATTAQUE NMAP:")
    print("-" * 40)
    
    local_ip = get_local_ip()
    print(f"1. 🌐 IP cible pour nmap: {local_ip}")
    print("2. 🔧 Depuis votre VM Kali, exécutez:")
    print(f"   nmap -sS -O -sV -p 1-1000 {local_ip}")
    print("   ou")
    print(f"   nmap -A -T4 {local_ip}")
    print("   ou pour un scan plus agressif:")
    print(f"   nmap -sS -sU -O -sV -sC -T5 {local_ip}")
    print()
    
    # Préparer la base
    if not setup_database():
        print("❌ Impossible de préparer la base de données")
        return
    
    print("🔄 OPTIONS DISPONIBLES:")
    print("1. Surveiller les nouvelles menaces en temps réel")
    print("2. Créer des alertes de test pour simulation")
    print("3. Afficher les commandes tcpdump pour monitoring manuel")
    print("4. Quitter")
    
    while True:
        try:
            choice = input("\n👉 Votre choix (1-4): ").strip()
            
            if choice == "1":
                print("\n🔍 DÉMARRAGE SURVEILLANCE TEMPS RÉEL")
                print("=" * 40)
                monitor_new_threats()
                break
                
            elif choice == "2":
                print("\n🧪 CRÉATION ALERTES DE TEST")
                print("=" * 30)
                create_test_alerts()
                print("✅ Alertes créées! Vérifiez le dashboard.")
                
            elif choice == "3":
                print("\n📡 COMMANDES MONITORING MANUEL")
                print("=" * 35)
                tcpdump_cmd, ip = start_network_monitoring()
                print(f"Exécutez dans un autre terminal:")
                print(f"  {' '.join(tcpdump_cmd)}")
                print()
                
            elif choice == "4":
                print("👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n👋 Arrêt du programme")
            break

if __name__ == "__main__":
    main()
