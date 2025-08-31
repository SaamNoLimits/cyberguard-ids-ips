import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import io
import psycopg2
from datetime import datetime, timedelta

print("🔴 DASHBOARD TEMPS RÉEL - DONNÉES DE LA BASE CYBERSÉCURITÉ")
print("=" * 65)

# Connexion à la base de données PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="cybersec_ids",
        user="cybersec",
        password="secure_password_123"
    )
    print("✅ Connexion à PostgreSQL réussie")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
    exit(1)

# Configuration du style
plt.style.use('dark_background')
sns.set_palette("husl")

# Création du dashboard en temps réel 2x3
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle(f'🛡️ Dashboard Cybersécurité Temps Réel - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 
             fontsize=16, fontweight='bold', color='white')

# 1. Statistiques globales (dernières 24h)
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        COUNT(*) as total_alerts,
        COUNT(CASE WHEN blocked = true THEN 1 END) as blocked_alerts,
        COUNT(DISTINCT source_ip) as unique_ips,
        COUNT(DISTINCT attack_type) as attack_types
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
""")
stats_24h = cursor.fetchone()

stats_labels = ['Total Alertes', 'Alertes Bloquées', 'IPs Uniques', 'Types d\'Attaques']
stats_values = list(stats_24h)
colors_stats = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12']

bars1 = ax1.bar(stats_labels, stats_values, color=colors_stats)
ax1.set_title('📊 Statistiques 24h', color='white', fontsize=12)
ax1.set_ylabel('Nombre', color='white')
ax1.tick_params(axis='x', rotation=45, colors='white')
ax1.tick_params(axis='y', colors='white')

# Valeurs sur les barres
for bar, value in zip(bars1, stats_values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + max(stats_values)*0.01,
             f'{value}', ha='center', va='bottom', color='white', fontweight='bold')

# 2. Distribution des types d'attaques (données réelles)
cursor.execute("""
    SELECT attack_type, COUNT(*) as count 
    FROM threat_alerts 
    GROUP BY attack_type 
    ORDER BY count DESC 
    LIMIT 8
""")
attack_types_data = cursor.fetchall()

if attack_types_data:
    attack_types = [row[0] for row in attack_types_data]
    attack_counts = [row[1] for row in attack_types_data]
    
    colors_attacks = plt.cm.Set3(np.linspace(0, 1, len(attack_types)))
    wedges, texts, autotexts = ax2.pie(attack_counts, labels=attack_types, autopct='%1.1f%%',
                                       colors=colors_attacks, startangle=90)
    ax2.set_title('🎯 Types d\'Attaques', color='white', fontsize=12)
    for text in texts:
        text.set_color('white')
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)

# 3. Timeline des alertes (dernières 24h par heure)
cursor.execute("""
    SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        COUNT(*) as alerts,
        COUNT(CASE WHEN blocked = true THEN 1 END) as blocked
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
    GROUP BY DATE_TRUNC('hour', timestamp)
    ORDER BY hour
""")
timeline_data = cursor.fetchall()

if timeline_data:
    hours = [row[0] for row in timeline_data]
    alert_counts = [row[1] for row in timeline_data]
    blocked_counts = [row[2] for row in timeline_data]
    
    # Formatage des heures pour l'affichage
    hour_labels = [h.strftime('%H:%M') if h else 'N/A' for h in hours]
    
    ax3.plot(range(len(hours)), alert_counts, marker='o', linewidth=2, 
             markersize=6, color='#e74c3c', label='Total')
    ax3.plot(range(len(hours)), blocked_counts, marker='s', linewidth=2, 
             markersize=4, color='#2ecc71', label='Bloquées')
    ax3.set_title('📈 Timeline 24h', color='white', fontsize=12)
    ax3.set_xlabel('Heure', color='white')
    ax3.set_ylabel('Alertes', color='white')
    ax3.tick_params(colors='white')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Étiquettes des heures (toutes les 4 heures)
    step = max(1, len(hour_labels) // 6)
    ax3.set_xticks(range(0, len(hour_labels), step))
    ax3.set_xticklabels([hour_labels[i] for i in range(0, len(hour_labels), step)])

# 4. Top 10 IPs sources
cursor.execute("""
    SELECT source_ip, COUNT(*) as count 
    FROM threat_alerts 
    WHERE source_ip IS NOT NULL 
    GROUP BY source_ip 
    ORDER BY count DESC 
    LIMIT 10
""")
top_ips_data = cursor.fetchall()

if top_ips_data:
    ips = [row[0] for row in top_ips_data]
    ip_counts = [row[1] for row in top_ips_data]
    
    colors_ips = plt.cm.Reds(np.linspace(0.4, 0.9, len(ips)))
    bars4 = ax4.barh(range(len(ips)), ip_counts, color=colors_ips)
    ax4.set_title('🌐 Top 10 IPs Sources', color='white', fontsize=12)
    ax4.set_xlabel('Nombre d\'Alertes', color='white')
    ax4.set_yticks(range(len(ips)))
    ax4.set_yticklabels(ips, color='white', fontsize=8)
    ax4.tick_params(colors='white')
    
    # Valeurs sur les barres
    for i, (bar, count) in enumerate(zip(bars4, ip_counts)):
        ax4.text(count + max(ip_counts)*0.01, i, str(count), 
                va='center', color='white', fontweight='bold', fontsize=8)

# 5. Distribution par niveau de menace
cursor.execute("""
    SELECT threat_level, COUNT(*) as count 
    FROM threat_alerts 
    GROUP BY threat_level 
    ORDER BY count DESC
""")
threat_levels_data = cursor.fetchall()

if threat_levels_data:
    levels = [row[0] for row in threat_levels_data]
    level_counts = [row[1] for row in threat_levels_data]
    
    level_colors = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12', 'LOW': '#2ecc71', 'CRITICAL': '#8e44ad'}
    colors_levels = [level_colors.get(level, '#95a5a6') for level in levels]
    
    bars5 = ax5.bar(levels, level_counts, color=colors_levels)
    ax5.set_title('⚠️ Niveaux de Menace', color='white', fontsize=12)
    ax5.set_ylabel('Nombre d\'Alertes', color='white')
    ax5.tick_params(colors='white')
    
    # Valeurs sur les barres
    for bar, count in zip(bars5, level_counts):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + max(level_counts)*0.01,
                 f'{count}', ha='center', va='bottom', color='white', fontweight='bold')

# 6. Heatmap activité par heure et jour de la semaine
cursor.execute("""
    SELECT 
        EXTRACT(DOW FROM timestamp) as day_of_week,
        EXTRACT(HOUR FROM timestamp) as hour,
        COUNT(*) as count
    FROM threat_alerts 
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY EXTRACT(DOW FROM timestamp), EXTRACT(HOUR FROM timestamp)
    ORDER BY day_of_week, hour
""")
heatmap_data = cursor.fetchall()

if heatmap_data:
    # Créer une matrice 7x24 (jours x heures)
    activity_matrix = np.zeros((7, 24))
    for row in heatmap_data:
        day, hour, count = row
        activity_matrix[int(day)][int(hour)] = count
    
    days = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
    hours_24 = [f'{i:02d}h' for i in range(24)]
    
    im = ax6.imshow(activity_matrix, cmap='Reds', aspect='auto')
    ax6.set_title('🔥 Activité 7j (Jour/Heure)', color='white', fontsize=12)
    ax6.set_xticks(range(0, 24, 4))
    ax6.set_xticklabels([hours_24[i] for i in range(0, 24, 4)], color='white')
    ax6.set_yticks(range(7))
    ax6.set_yticklabels(days, color='white')
    ax6.tick_params(colors='white')

plt.tight_layout()

# Conversion en base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
            facecolor='#1a1a1a', edgecolor='none')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

# Statistiques finales
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        MIN(timestamp) as first_alert,
        MAX(timestamp) as last_alert,
        COUNT(DISTINCT source_ip) as unique_sources
    FROM threat_alerts
""")
final_stats = cursor.fetchone()

print("\n📋 STATISTIQUES GLOBALES:")
print(f"   • Total alertes: {final_stats[0]:,}")
print(f"   • Première alerte: {final_stats[1]}")
print(f"   • Dernière alerte: {final_stats[2]}")
print(f"   • Sources uniques: {final_stats[3]}")

if stats_24h:
    print(f"\n⏰ DERNIÈRES 24H:")
    print(f"   • Alertes: {stats_24h[0]:,}")
    print(f"   • Bloquées: {stats_24h[1]:,}")
    print(f"   • IPs uniques: {stats_24h[2]}")
    print(f"   • Types d'attaques: {stats_24h[3]}")

print(f"\n🖼️ Dashboard temps réel généré!")
print(f"📊 6 graphiques avec données PostgreSQL en direct")
print(f"IMAGE_BASE64:{image_base64}")

conn.close()
print("✅ Analyse temps réel terminée!")
