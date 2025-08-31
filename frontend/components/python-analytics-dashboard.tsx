"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Play, 
  Code, 
  Database, 
  BarChart3, 
  Image as ImageIcon,
  Save,
  History,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Download
} from 'lucide-react'

interface PythonResult {
  success: boolean
  output?: string
  error?: string
  execution_time: number
  images?: string[]
  timestamp?: string
  generated_files?: string[]
}

interface ScriptHistory {
  id: number
  timestamp: string
  query_type: string
  query_text: string
  result: string
  execution_time: number
  success: boolean
}

export default function PythonAnalyticsDashboard() {
  const [mounted, setMounted] = useState(false)
  const [code, setCode] = useState('')
  const [result, setResult] = useState<PythonResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<ScriptHistory[]>([])

  useEffect(() => {
    setMounted(true)
  }, [])

  // Sample Python scripts for cybersecurity analysis
  const sampleScripts = [
    {
      name: "🛡️ Dashboard Cybersécurité Temps Réel",
      code: `# 🛡️ DASHBOARD CYBERSÉCURITÉ - DONNÉES TEMPS RÉEL
# Script utilisant les vraies données PostgreSQL

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import io
import psycopg2
from datetime import datetime, timedelta

print("🔴 DASHBOARD CYBERSÉCURITÉ - DONNÉES TEMPS RÉEL")
print("=" * 55)
print(f"📅 Analyse générée le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")

# Connexion à PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="cybersec_ids", 
        user="cybersec",
        password="secure_password_123"
    )
    print("✅ Connexion PostgreSQL réussie")
except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)

# Style sombre pour le dashboard
plt.style.use('dark_background')
sns.set_palette("husl")

# Dashboard 2x2 avec données réelles
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('🛡️ Dashboard Cybersécurité - Données PostgreSQL Temps Réel', 
             fontsize=16, fontweight='bold', color='white')

cursor = conn.cursor()

# 1. TOP 10 TYPES D'ATTAQUES (Données réelles)
cursor.execute("""
    SELECT attack_type, COUNT(*) as count 
    FROM threat_alerts 
    GROUP BY attack_type 
    ORDER BY count DESC 
    LIMIT 10
""")
attack_data = cursor.fetchall()

if attack_data:
    attack_types = [row[0][:15] + '...' if len(row[0]) > 15 else row[0] for row in attack_data]
    attack_counts = [row[1] for row in attack_data]
    
    colors1 = plt.cm.Set3(np.linspace(0, 1, len(attack_types)))
    bars1 = ax1.bar(range(len(attack_types)), attack_counts, color=colors1)
    ax1.set_title('🎯 Top 10 Types d\'Attaques', color='white', fontweight='bold')
    ax1.set_ylabel('Nombre d\'Alertes', color='white')
    ax1.set_xticks(range(len(attack_types)))
    ax1.set_xticklabels(attack_types, rotation=45, ha='right', color='white', fontsize=9)
    ax1.tick_params(colors='white')
    
    # Valeurs sur les barres
    for i, (bar, count) in enumerate(zip(bars1, attack_counts)):
        height = bar.get_height()
        ax1.text(i, height + max(attack_counts)*0.01, f'{count:,}', 
                ha='center', va='bottom', color='white', fontweight='bold', fontsize=9)
    
    print(f"📊 Types d'attaques analysés: {len(attack_data)}")
    print(f"🎯 Type dominant: {attack_data[0][0]} ({attack_data[0][1]:,} alertes)")

# 2. RÉPARTITION PAR NIVEAU DE MENACE
cursor.execute("""
    SELECT threat_level, COUNT(*) as count 
    FROM threat_alerts 
    GROUP BY threat_level 
    ORDER BY count DESC
""")
threat_levels = cursor.fetchall()

if threat_levels:
    levels = [row[0] for row in threat_levels]
    level_counts = [row[1] for row in threat_levels]
    
    # Couleurs par niveau de menace
    level_colors = {
        'CRITICAL': '#8e44ad', 'HIGH': '#e74c3c', 
        'MEDIUM': '#f39c12', 'LOW': '#2ecc71'
    }
    colors2 = [level_colors.get(level, '#95a5a6') for level in levels]
    
    wedges, texts, autotexts = ax2.pie(level_counts, labels=levels, autopct='%1.1f%%',
                                       colors=colors2, startangle=90)
    ax2.set_title('⚠️ Répartition par Niveau de Menace', color='white', fontweight='bold')
    
    for text in texts:
        text.set_color('white')
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    print(f"⚠️ Niveaux de menace: {len(threat_levels)}")
    print(f"🚨 Niveau dominant: {threat_levels[0][0]} ({threat_levels[0][1]:,} alertes)")

# 3. TIMELINE DES ALERTES (24 dernières heures)
cursor.execute("""
    SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        COUNT(*) as total,
        COUNT(CASE WHEN blocked = true THEN 1 END) as blocked
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
    GROUP BY DATE_TRUNC('hour', timestamp)
    ORDER BY hour
""")
timeline = cursor.fetchall()

if timeline:
    hours = [row[0] for row in timeline]
    totals = [row[1] for row in timeline]
    blocked = [row[2] for row in timeline]
    
    # Formatage pour affichage
    hour_labels = [h.strftime('%H:%M') for h in hours]
    x_pos = range(len(hours))
    
    ax3.plot(x_pos, totals, marker='o', linewidth=3, markersize=8, 
             color='#e74c3c', label='Total Alertes', markerfacecolor='#f39c12')
    ax3.plot(x_pos, blocked, marker='s', linewidth=2, markersize=6, 
             color='#2ecc71', label='Bloquées', alpha=0.8)
    ax3.fill_between(x_pos, totals, alpha=0.3, color='#e74c3c')
    
    ax3.set_title('📈 Timeline 24h (Données Réelles)', color='white', fontweight='bold')
    ax3.set_xlabel('Heure', color='white')
    ax3.set_ylabel('Nombre d\'Alertes', color='white')
    ax3.tick_params(colors='white')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    
    # Étiquettes des heures
    step = max(1, len(hour_labels) // 6)
    ax3.set_xticks(range(0, len(hour_labels), step))
    ax3.set_xticklabels([hour_labels[i] for i in range(0, len(hour_labels), step)])
    
    print(f"📈 Points temporels: {len(timeline)}")
    if timeline:
        max_hour = max(timeline, key=lambda x: x[1])
        print(f"🔥 Pic d'activité: {max_hour[0].strftime('%H:%M')} ({max_hour[1]} alertes)")

# 4. TOP 15 ADRESSES IP SOURCES
cursor.execute("""
    SELECT source_ip, COUNT(*) as count 
    FROM threat_alerts 
    WHERE source_ip IS NOT NULL 
    GROUP BY source_ip 
    ORDER BY count DESC 
    LIMIT 15
""")
top_ips = cursor.fetchall()

if top_ips:
    ips = [row[0] for row in top_ips]
    ip_counts = [row[1] for row in top_ips]
    
    colors4 = plt.cm.Reds(np.linspace(0.4, 0.9, len(ips)))
    bars4 = ax4.barh(range(len(ips)), ip_counts, color=colors4)
    
    ax4.set_title('🌐 Top 15 IPs Sources', color='white', fontweight='bold')
    ax4.set_xlabel('Nombre d\'Alertes', color='white')
    ax4.set_yticks(range(len(ips)))
    ax4.set_yticklabels(ips, color='white', fontsize=8)
    ax4.tick_params(colors='white')
    
    # Valeurs sur les barres
    for i, (bar, count) in enumerate(zip(bars4, ip_counts)):
        ax4.text(count + max(ip_counts)*0.01, i, f'{count:,}', 
                va='center', color='white', fontweight='bold', fontsize=8)
    
    print(f"🌐 IPs sources uniques: {len(top_ips)}")
    print(f"🥇 IP la plus active: {top_ips[0][0]} ({top_ips[0][1]:,} alertes)")

plt.tight_layout()

# Conversion en base64 pour affichage web
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
            facecolor='#1a1a1a', edgecolor='none')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

# STATISTIQUES GLOBALES
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT source_ip) as unique_ips,
        COUNT(DISTINCT attack_type) as attack_types,
        COUNT(CASE WHEN blocked = true THEN 1 END) as blocked,
        MIN(timestamp) as first_alert,
        MAX(timestamp) as last_alert
    FROM threat_alerts
""")
global_stats = cursor.fetchone()

cursor.execute("""
    SELECT COUNT(*) 
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
""")
alerts_24h = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '1 hour'
""")
alerts_1h = cursor.fetchone()[0]

print("\n" + "="*55)
print("📊 STATISTIQUES GLOBALES DE LA BASE:")
print("="*55)
print(f"📈 Total alertes: {global_stats[0]:,}")
print(f"🌐 IPs sources uniques: {global_stats[1]:,}")
print(f"🎯 Types d'attaques: {global_stats[2]}")
print(f"🛡️ Alertes bloquées: {global_stats[4]:,}")
print(f"📅 Première alerte: {global_stats[5]}")
print(f"📅 Dernière alerte: {global_stats[6]}")

print(f"\n⏰ ACTIVITÉ RÉCENTE:")
print(f"📊 Dernières 24h: {alerts_24h:,} alertes")
print(f"🔥 Dernière heure: {alerts_1h:,} alertes")

# Calcul du taux d'activité
if global_stats[5] and global_stats[6]:
    time_diff = global_stats[6] - global_stats[5]
    days_diff = time_diff.total_seconds() / (24 * 3600)
    avg_per_day = global_stats[0] / days_diff if days_diff > 0 else 0
    print(f"📈 Moyenne: {avg_per_day:.0f} alertes/jour")

print(f"\n🖼️ Dashboard généré avec {len(attack_data) if attack_data else 0} types d'attaques")
print(f"📊 Données extraites de PostgreSQL en temps réel")
print(f"IMAGE_BASE64:{image_base64}")

conn.close()
print("\n✅ Analyse terminée - Dashboard prêt pour affichage!")`
    },
    {
      name: "Test Simple - Génération d'Image",
      code: `# Test simple de génération d'image
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

print("=== TEST GÉNÉRATION IMAGE ===")
print("Création d'un graphique simple...")

# Données simples
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Création du graphique
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'bo-', linewidth=2, markersize=8)
plt.title('Test Simple - Ligne Droite')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True, alpha=0.3)

# Conversion en base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("✅ Graphique créé avec succès!")
print(f"📊 Taille de l'image: {len(image_base64)} caractères")
print(f"IMAGE_BASE64:{image_base64}")
print("🖼️  Image prête pour affichage!")`
    },
    {
      name: "Analyse des Menaces - Statistiques",
      code: `# Analyse statistique des menaces de cybersécurité
import json
from datetime import datetime, timedelta

print("=== ANALYSE STATISTIQUE DES MENACES ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Simulation de données de menaces
threat_data = {
    "total_threats": 10,
    "high_risk": 8,
    "medium_risk": 2,
    "attack_types": {
        "Flood Attacks": 8,
        "Reconnaissance": 2
    },
    "top_source_ips": [
        "192.168.100.200",
        "216.58.215.164",
        "34.160.144.191"
    ]
}

print(f"\\n📊 STATISTIQUES GÉNÉRALES:")
print(f"- Total des menaces: {threat_data['total_threats']}")
print(f"- Menaces critiques: {threat_data['high_risk']}")
print(f"- Menaces moyennes: {threat_data['medium_risk']}")

print(f"\\n🎯 TYPES D'ATTAQUES:")
for attack_type, count in threat_data['attack_types'].items():
    percentage = (count / threat_data['total_threats']) * 100
    print(f"- {attack_type}: {count} ({percentage:.1f}%)")

print(f"\\n🌐 TOP IPs SOURCES:")
for i, ip in enumerate(threat_data['top_source_ips'][:3], 1):
    print(f"{i}. {ip}")

# Calcul du score de risque
risk_score = (threat_data['high_risk'] * 3 + threat_data['medium_risk'] * 2) / threat_data['total_threats']
print(f"\\n⚠️  SCORE DE RISQUE: {risk_score:.1f}/3.0")

if risk_score > 2.5:
    print("🚨 NIVEAU D'ALERTE: CRITIQUE")
    print("Recommandations:")
    print("- Bloquer immédiatement les IPs suspectes")
    print("- Activer la surveillance renforcée")
    print("- Notifier l'équipe de sécurité")
elif risk_score > 1.5:
    print("🟡 NIVEAU D'ALERTE: ÉLEVÉ")
    print("Recommandations:")
    print("- Surveiller les patterns d'attaque")
    print("- Renforcer les règles de firewall")
else:
    print("🟢 NIVEAU D'ALERTE: NORMAL")
    print("- Surveillance de routine")

print(f"\\n✅ Analyse terminée à {datetime.now().strftime('%H:%M:%S')}")`
    },
    {
      name: "Analyse Temporelle des Attaques",
      code: `# Analyse temporelle des patterns d'attaque
import json
from datetime import datetime, timedelta
import random

print("=== ANALYSE TEMPORELLE DES ATTAQUES ===")

# Simulation d'analyse temporelle
hours = []
attack_counts = []

print("📈 DISTRIBUTION HORAIRE DES ATTAQUES (dernières 24h):")
print("Heure    | Attaques | Graphique")
print("-" * 35)

for hour in range(24):
    # Simulation de données avec plus d'attaques la nuit
    if 22 <= hour or hour <= 6:
        count = random.randint(15, 30)  # Plus d'attaques la nuit
    else:
        count = random.randint(5, 15)   # Moins d'attaques le jour
    
    hours.append(f"{hour:02d}:00")
    attack_counts.append(count)
    
    # Graphique ASCII simple
    bar = "█" * (count // 3)
    print(f"{hour:02d}:00    | {count:8d} | {bar}")

total_attacks = sum(attack_counts)
peak_hour = hours[attack_counts.index(max(attack_counts))]
min_hour = hours[attack_counts.index(min(attack_counts))]

print(f"\\n📊 RÉSUMÉ:")
print(f"- Total attaques 24h: {total_attacks}")
print(f"- Pic d'activité: {peak_hour} ({max(attack_counts)} attaques)")
print(f"- Minimum d'activité: {min_hour} ({min(attack_counts)} attaques)")
print(f"- Moyenne horaire: {total_attacks/24:.1f} attaques")

# Détection de patterns
night_attacks = sum(attack_counts[22:] + attack_counts[:7])
day_attacks = total_attacks - night_attacks

print(f"\\n🌙 ANALYSE JOUR/NUIT:")
print(f"- Attaques nocturnes (22h-7h): {night_attacks} ({night_attacks/total_attacks*100:.1f}%)")
print(f"- Attaques diurnes (7h-22h): {day_attacks} ({day_attacks/total_attacks*100:.1f}%)")

if night_attacks > day_attacks * 1.5:
    print("⚠️  ALERTE: Activité suspecte nocturne détectée!")
    print("Recommandation: Renforcer la surveillance nocturne")

print(f"\\n✅ Analyse temporelle terminée")`
    },
    {
      name: "Génération de Graphiques (Matplotlib)",
      code: `# Génération de graphiques pour l'analyse de cybersécurité
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import io
import base64

print("=== GÉNÉRATION DE GRAPHIQUES D'ANALYSE ===")

# Configuration pour éviter l'affichage GUI
plt.switch_backend('Agg')

# Données simulées
attack_types = ['Flood Attacks', 'Port Scan', 'Reconnaissance', 'Malware', 'Phishing']
attack_counts = [45, 23, 18, 12, 8]
colors = ['#ff4444', '#ff8800', '#ffaa00', '#88aa00', '#0088aa']

# Graphique 1: Camembert des types d'attaques
plt.figure(figsize=(10, 6))

plt.subplot(1, 2, 1)
plt.pie(attack_counts, labels=attack_types, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('Distribution des Types d\\'Attaques')

# Graphique 2: Barres des attaques par type
plt.subplot(1, 2, 2)
bars = plt.bar(attack_types, attack_counts, color=colors)
plt.title('Nombre d\\'Attaques par Type')
plt.xlabel('Type d\\'Attaque')
plt.ylabel('Nombre d\\'Attaques')
plt.xticks(rotation=45, ha='right')

# Ajouter les valeurs sur les barres
for bar, count in zip(bars, attack_counts):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             str(count), ha='center', va='bottom')

plt.tight_layout()

# Sauvegarder le graphique
plt.savefig('/tmp/cybersec_analysis.png', dpi=300, bbox_inches='tight')
print("📊 Graphique sauvegardé: /tmp/cybersec_analysis.png")

# Graphique temporel
plt.figure(figsize=(12, 4))
hours = list(range(24))
attacks_per_hour = np.random.poisson(8, 24)  # Distribution de Poisson

plt.plot(hours, attacks_per_hour, marker='o', linewidth=2, markersize=4)
plt.fill_between(hours, attacks_per_hour, alpha=0.3)
plt.title('Évolution des Attaques sur 24h')
plt.xlabel('Heure')
plt.ylabel('Nombre d\\'Attaques')
plt.grid(True, alpha=0.3)
plt.xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig('/tmp/cybersec_timeline.png', dpi=300, bbox_inches='tight')
print("📈 Timeline sauvegardée: /tmp/cybersec_timeline.png")

plt.close('all')  # Fermer toutes les figures

print("\\n✅ Génération de graphiques terminée!")
print("Les fichiers sont disponibles dans /tmp/")
print("- cybersec_analysis.png: Analyse des types d'attaques")
print("- cybersec_timeline.png: Évolution temporelle")`
    },
    {
      name: "Analyse de Géolocalisation des IPs",
      code: `# Analyse géographique des sources d'attaque
import json
from datetime import datetime
import random

print("=== ANALYSE GÉOGRAPHIQUE DES ATTAQUES ===")

# Simulation de données de géolocalisation
ip_locations = {
    "192.168.100.200": {"country": "Local Network", "city": "LAN", "lat": 0, "lon": 0},
    "216.58.215.164": {"country": "United States", "city": "Mountain View", "lat": 37.4, "lon": -122.1},
    "34.160.144.191": {"country": "United States", "city": "Council Bluffs", "lat": 41.2, "lon": -95.9},
    "185.220.101.182": {"country": "Germany", "city": "Frankfurt", "lat": 50.1, "lon": 8.7},
    "103.28.248.25": {"country": "Singapore", "city": "Singapore", "lat": 1.3, "lon": 103.8},
    "45.227.255.190": {"country": "Brazil", "city": "São Paulo", "lat": -23.5, "lon": -46.6}
}

attack_data = []
for ip, location in ip_locations.items():
    attacks = random.randint(5, 25)
    attack_data.append({
        "ip": ip,
        "attacks": attacks,
        "country": location["country"],
        "city": location["city"],
        "coordinates": [location["lat"], location["lon"]]
    })

# Trier par nombre d'attaques
attack_data.sort(key=lambda x: x["attacks"], reverse=True)

print("🌍 TOP PAYS SOURCES D'ATTAQUES:")
print("Rang | Pays              | Ville           | IP              | Attaques")
print("-" * 75)

country_stats = {}
for i, data in enumerate(attack_data, 1):
    country = data["country"]
    if country not in country_stats:
        country_stats[country] = 0
    country_stats[country] += data["attacks"]
    
    print(f"{i:4d} | {data['country']:17s} | {data['city']:15s} | {data['ip']:15s} | {data['attacks']:8d}")

print(f"\\n📊 STATISTIQUES PAR PAYS:")
for country, total in sorted(country_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (total / sum(country_stats.values())) * 100
    print(f"- {country}: {total} attaques ({percentage:.1f}%)")

# Analyse des zones à risque
high_risk_countries = [country for country, attacks in country_stats.items() if attacks > 15]
print(f"\\n⚠️  ZONES À HAUT RISQUE ({len(high_risk_countries)} pays):")
for country in high_risk_countries:
    print(f"- {country}: {country_stats[country]} attaques")

# Recommandations géographiques
print(f"\\n🛡️  RECOMMANDATIONS:")
if len(high_risk_countries) > 0:
    print("- Considérer le blocage géographique pour les pays à haut risque")
    print("- Mettre en place une surveillance renforcée pour ces régions")
    print("- Analyser les patterns d'attaque par fuseau horaire")

print(f"\\n🌐 COORDONNÉES POUR CARTOGRAPHIE:")
for data in attack_data[:3]:  # Top 3
    print(f"- {data['city']}, {data['country']}: [{data['coordinates'][0]:.1f}, {data['coordinates'][1]:.1f}]")

print(f"\n✅ Analyse géographique terminée à {datetime.now().strftime('%H:%M:%S')}")`
    },
    {
      name: "Graphiques de Cybersécurité",
      code: `# Génération de graphiques d'analyse cybersécurité
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import base64
import io
from datetime import datetime, timedelta

print("=== GÉNÉRATION DE GRAPHIQUES CYBERSÉCURITÉ ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Configuration du style
plt.style.use('dark_background')
sns.set_palette("husl")

# Données simulées de menaces
threat_types = ['Port Scan', 'DDoS', 'Malware', 'Phishing', 'Injection', 'Brute Force']
threat_counts = [45, 23, 12, 8, 15, 18]

# Données temporelles (dernières 24h)
hours = list(range(24))
attack_timeline = np.random.poisson(5, 24)  # Distribution de Poisson pour les attaques
attack_timeline[22:] += np.random.poisson(10, 2)  # Plus d'attaques la nuit
attack_timeline[:6] += np.random.poisson(8, 6)

# Création du dashboard avec 4 graphiques
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Dashboard Cybersécurité - Analyse des Menaces', fontsize=16, fontweight='bold', color='white')

# 1. Graphique en barres - Types de menaces
colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff', '#5f27cd']
bars = ax1.bar(threat_types, threat_counts, color=colors)
ax1.set_title('Distribution des Types de Menaces', color='white')
ax1.set_ylabel('Nombre de Menaces', color='white')
ax1.tick_params(axis='x', rotation=45, colors='white')
ax1.tick_params(axis='y', colors='white')

# Ajout des valeurs sur les barres
for bar, count in zip(bars, threat_counts):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{count}', ha='center', va='bottom', color='white')

# 2. Graphique en secteurs - Répartition des menaces
wedges, texts, autotexts = ax2.pie(threat_counts, labels=threat_types, autopct='%1.1f%%', 
                                   colors=colors, startangle=90)
ax2.set_title('Répartition des Menaces par Type', color='white')
for text in texts:
    text.set_color('white')
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')

# 3. Timeline des attaques (24h)
ax3.plot(hours, attack_timeline, marker='o', linewidth=2, markersize=6, 
         color='#ff6b6b', markerfacecolor='#feca57')
ax3.fill_between(hours, attack_timeline, alpha=0.3, color='#ff6b6b')
ax3.set_title('Timeline des Attaques (24h)', color='white')
ax3.set_xlabel('Heure', color='white')
ax3.set_ylabel('Nombre d\'Attaques', color='white')
ax3.tick_params(colors='white')
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 23)

# 4. Heatmap de sévérité
severity_data = np.random.rand(6, 4) * 100  # 6 types, 4 niveaux de sévérité
severity_labels = ['Critique', 'Élevé', 'Moyen', 'Faible']
im = ax4.imshow(severity_data, cmap='Reds', aspect='auto')
ax4.set_title('Matrice de Sévérité des Menaces', color='white')
ax4.set_xticks(range(len(severity_labels)))
ax4.set_xticklabels(severity_labels, color='white')
ax4.set_yticks(range(len(threat_types)))
ax4.set_yticklabels(threat_types, color='white')

# Ajout des valeurs dans la heatmap
for i in range(len(threat_types)):
    for j in range(len(severity_labels)):
        text = ax4.text(j, i, f'{severity_data[i, j]:.0f}',
                       ha="center", va="center", color="white", fontweight='bold')

plt.tight_layout()

# Conversion en base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
            facecolor='#1a1a1a', edgecolor='none')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("📊 Dashboard généré avec succès!")
print("📈 Graphiques inclus:")
print("   - Distribution des types de menaces")
print("   - Répartition en secteurs")
print("   - Timeline des attaques 24h")
print("   - Matrice de sévérité")
print(f"🖼️  Image encodée en base64 ({len(image_base64)} caractères)")
print(f"IMAGE_BASE64:{image_base64}")

# Statistiques résumées
total_threats = sum(threat_counts)
max_threat_type = threat_types[threat_counts.index(max(threat_counts))]
max_attacks_hour = hours[np.argmax(attack_timeline)]

print(f"\n📋 RÉSUMÉ ANALYTIQUE:")
print(f"   - Total des menaces: {total_threats}")
print(f"   - Type le plus fréquent: {max_threat_type} ({max(threat_counts)} occurrences)")
print(f"   - Pic d'activité: {max_attacks_hour}h00 ({max(attack_timeline)} attaques)")
print(f"   - Moyenne horaire: {np.mean(attack_timeline):.1f} attaques/h")

print(f"\n✅ Analyse complète terminée à {datetime.now().strftime('%H:%M:%S')}")`
    }
  ]

  const loadHistory = async () => {
    try {
      // History endpoint not available in current backend
      // const response = await fetch('http://localhost:8000/api/query/history?limit=10')
      // const data = await response.json()
      const data = []
      setHistory(data.filter((item: ScriptHistory) => item.query_type === 'Python'))
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

const executeCode = async () => {
  if (!code.trim()) return
  
  setLoading(true)
  setResult(null)
  
  try {
    const response = await fetch('http://localhost:8000/api/python/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    })
    
    const data = await response.json()
    
    // Extract images from output if present
    if (data.success && data.output) {
      const images: string[] = []
      const lines = data.output.split('\n')
      
      console.log('Python result lines:', lines.length)
      console.log('Looking for IMAGE_BASE64 lines...')
      
      lines.forEach((line: string) => {
        if (line.startsWith('IMAGE_BASE64:')) {
          console.log('Found IMAGE_BASE64 line!')
          const base64Data = line.replace('IMAGE_BASE64:', '')
          images.push(base64Data)
          console.log('Added image, total images:', images.length)
        }
      })
      
      data.images = images
      console.log('Final images array:', data.images?.length || 0)
    }
    
    setResult(data)
    
    // Reload history after execution (disabled for now)
    // await loadHistory()
  } catch (error) {
    setResult({
      success: false,
      error: error instanceof Error ? error.message : 'Erreur inconnue',
      execution_time: 0
    })
  } finally {
    setLoading(false)
  }
}

  const loadSampleScript = (script: typeof sampleScripts[0]) => {
    setCode(script.code)
    setResult(null)
  }

  useEffect(() => {
    loadHistory()
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading Python Analytics Dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Code className="w-8 h-8 text-blue-500" />
              Python Analytics & Cybersecurity
            </h1>
            <p className="text-muted-foreground mt-2">
              Exécutez des scripts Python avancés pour l'analyse de cybersécurité avec support d'images
            </p>
          </div>
          <Badge variant="outline" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            PostgreSQL Connected
          </Badge>
        </div>

        <Tabs defaultValue="editor" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="editor" className="flex items-center gap-2">
              <Code className="w-4 h-4" />
              Python Editor
            </TabsTrigger>
            <TabsTrigger value="samples" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Sample Scripts
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="w-4 h-4" />
              Execution History
            </TabsTrigger>
          </TabsList>

          {/* Python Editor Tab */}
          <TabsContent value="editor" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Code Editor */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Python Code Editor
                  </CardTitle>
                  <CardDescription>
                    Écrivez et exécutez des scripts Python pour l'analyse de cybersécurité
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="# Entrez votre code Python ici...
import pandas as pd
import matplotlib.pyplot as plt

print('Hello Cybersecurity Analytics!')"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="min-h-80 font-mono text-sm"
                  />
                  <div className="flex gap-2">
                    <Button 
                      onClick={executeCode} 
                      disabled={loading || !code.trim()}
                      className="flex items-center gap-2"
                    >
                      <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                      {loading ? 'Exécution...' : 'Exécuter Python'}
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => setCode('')}
                      className="flex items-center gap-2"
                    >
                      Clear
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {result?.success ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : result?.success === false ? (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    ) : (
                      <FileText className="w-5 h-5" />
                    )}
                    Résultats d'Exécution
                  </CardTitle>
                  {result && (
                    <CardDescription>
                      Temps d'exécution: {result.execution_time.toFixed(4)}s
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  {result ? (
                    <div className="space-y-4">
                      {result.success ? (
                        <div className="space-y-4">
                          {/* Text Output */}
                          <div className="bg-gray-900 text-green-400 rounded-lg p-4 overflow-auto max-h-80">
                            <pre className="text-sm whitespace-pre-wrap">
                              {result.output}
                            </pre>
                          </div>
                          
                          {/* Images (if any) */}
                          {result.images && result.images.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="font-medium flex items-center gap-2">
                                <ImageIcon className="w-4 h-4" />
                                Images générées ({result.images.length})
                              </h4>
                              <div className="grid grid-cols-1 gap-4">
                                {result.images.map((image, index) => (
                                  <div key={index} className="border rounded-lg p-2">
                                    <img 
                                      src={`data:image/png;base64,${image}`} 
                                      alt={`Generated chart ${index + 1}`}
                                      className="max-w-full h-auto rounded"
                                    />
                                    <div className="mt-2 flex justify-end">
                                      <Button size="sm" variant="outline">
                                        <Download className="w-4 h-4 mr-2" />
                                        Télécharger
                                      </Button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            <strong>Erreur d'exécution:</strong><br />
                            {result.error}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">
                      Aucun résultat pour le moment. Exécutez du code Python pour voir les résultats.
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Sample Scripts Tab */}
          <TabsContent value="samples" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {sampleScripts.map((script, index) => (
                <Card key={index} className="cursor-pointer hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{script.name}</CardTitle>
                    <CardDescription>
                      Script d'exemple pour l'analyse de cybersécurité
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted rounded p-3 mb-4">
                      <code className="text-sm">
                        {script.code.split('\n').slice(0, 3).join('\n')}...
                      </code>
                    </div>
                    <Button 
                      onClick={() => loadSampleScript(script)}
                      className="w-full"
                    >
                      Charger ce Script
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  Historique des Exécutions Python
                </CardTitle>
                <CardDescription>
                  Historique des scripts Python exécutés récemment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {history.length > 0 ? (
                    history.map((entry) => (
                      <div key={entry.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">Python</Badge>
                            {entry.success ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-red-500" />
                            )}
                            <span className="text-sm text-muted-foreground">
                              {entry.execution_time.toFixed(4)}s
                            </span>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            {mounted ? new Date(entry.timestamp).toLocaleString() : entry.timestamp}
                          </span>
                        </div>
                        <div className="bg-muted rounded p-2 mb-2">
                          <code className="text-sm">
                            {entry.query_text.substring(0, 150)}
                            {entry.query_text.length > 150 && '...'}
                          </code>
                        </div>
                        {entry.success && (
                          <div className="text-sm text-muted-foreground">
                            Résultat: {entry.result.substring(0, 100)}...
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-muted-foreground">
                      Aucun historique d'exécution Python pour le moment.
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
