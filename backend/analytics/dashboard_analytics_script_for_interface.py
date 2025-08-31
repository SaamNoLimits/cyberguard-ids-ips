# 🛡️ DASHBOARD CYBERSÉCURITÉ - DONNÉES TEMPS RÉEL
# Script à utiliser dans l'interface Analytics pour voir les vraies données

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
print("\n✅ Analyse terminée - Dashboard prêt pour affichage!")
