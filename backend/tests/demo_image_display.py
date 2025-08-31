#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to test image display in the cybersecurity platform
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import base64
import io

print("🚀 DEMO: Cybersecurity Analytics with Image Generation")
print("=" * 60)

# Set style for better visuals
plt.style.use('dark_background')
sns.set_palette("husl")

# Create comprehensive cybersecurity dashboard
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('🛡️ Cybersecurity Threat Analytics Dashboard', fontsize=16, fontweight='bold', color='white')

# 1. Threat Types Distribution
threat_types = ['Port Scan', 'DDoS', 'Malware', 'Phishing', 'Injection', 'Brute Force']
threat_counts = [45, 23, 12, 8, 15, 18]
colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff', '#5f27cd']

bars = ax1.bar(threat_types, threat_counts, color=colors)
ax1.set_title('🎯 Threat Types Distribution', color='white', fontsize=12)
ax1.set_ylabel('Number of Threats', color='white')
ax1.tick_params(axis='x', rotation=45, colors='white')
ax1.tick_params(axis='y', colors='white')

# Add values on bars
for bar, count in zip(bars, threat_counts):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{count}', ha='center', va='bottom', color='white', fontweight='bold')

# 2. Threat Level Pie Chart
threat_levels = ['Critical', 'High', 'Medium', 'Low']
level_counts = [25, 35, 30, 10]
level_colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']

wedges, texts, autotexts = ax2.pie(level_counts, labels=threat_levels, autopct='%1.1f%%', 
                                   colors=level_colors, startangle=90)
ax2.set_title('⚠️ Threat Severity Levels', color='white', fontsize=12)
for text in texts:
    text.set_color('white')
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')

# 3. Attack Timeline (24h)
hours = list(range(24))
attack_timeline = np.random.poisson(5, 24)
attack_timeline[22:] += np.random.poisson(10, 2)  # More attacks at night
attack_timeline[:6] += np.random.poisson(8, 6)

ax3.plot(hours, attack_timeline, marker='o', linewidth=2, markersize=6, 
         color='#e74c3c', markerfacecolor='#f39c12')
ax3.fill_between(hours, attack_timeline, alpha=0.3, color='#e74c3c')
ax3.set_title('📈 Attack Timeline (24h)', color='white', fontsize=12)
ax3.set_xlabel('Hour', color='white')
ax3.set_ylabel('Number of Attacks', color='white')
ax3.tick_params(colors='white')
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 23)

# 4. Geographic Heatmap
countries = ['USA', 'China', 'Russia', 'Germany', 'Brazil', 'India']
attack_sources = np.random.rand(6, 4) * 100
severity_labels = ['Critical', 'High', 'Medium', 'Low']

im = ax4.imshow(attack_sources, cmap='Reds', aspect='auto')
ax4.set_title('🌍 Geographic Attack Sources', color='white', fontsize=12)
ax4.set_xticks(range(len(severity_labels)))
ax4.set_xticklabels(severity_labels, color='white')
ax4.set_yticks(range(len(countries)))
ax4.set_yticklabels(countries, color='white')

# Add values in heatmap
for i in range(len(countries)):
    for j in range(len(severity_labels)):
        text = ax4.text(j, i, f'{attack_sources[i, j]:.0f}',
                       ha="center", va="center", color="white", fontweight='bold')

plt.tight_layout()

# Convert to base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
            facecolor='#1a1a1a', edgecolor='none')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("✅ Dashboard generated successfully!")
print("📊 Charts included:")
print("   • Threat types distribution")
print("   • Threat severity levels")
print("   • 24-hour attack timeline")
print("   • Geographic attack sources")
print(f"🖼️  Image size: {len(image_base64)} characters")
print("")
print("🎯 DISPLAYING IMAGE:")
print(f"IMAGE_BASE64:{image_base64}")
print("")
print("✨ Demo completed! Image should appear in the frontend.")
print("🌐 Check http://localhost:3000/analytics to see the visualization!")
