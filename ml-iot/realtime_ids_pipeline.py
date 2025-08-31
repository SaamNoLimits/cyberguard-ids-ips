#!/usr/bin/env python3
"""
Real-time IoT IDS Pipeline
Detects attacks from Kali VM and logs to dashboard + blockchain
"""

import pandas as pd
import numpy as np
import pickle
import json
import time
import threading
from datetime import datetime, timedelta
from collections import deque
import sqlite3
import hashlib
import socket
import struct
from scapy.all import sniff, IP, TCP, UDP, ICMP
import logging
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ids_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BlockchainAudit:
    """Simple blockchain for audit trail"""
    
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block"""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now().isoformat(),
            'data': 'Genesis Block - IoT IDS Started',
            'previous_hash': '0',
            'hash': self.calculate_hash('0', 'Genesis Block - IoT IDS Started', datetime.now().isoformat())
        }
        self.chain.append(genesis_block)
        logger.info("🔗 Blockchain initialized with genesis block")
    
    def calculate_hash(self, previous_hash, data, timestamp):
        """Calculate SHA-256 hash"""
        value = f"{previous_hash}{data}{timestamp}"
        return hashlib.sha256(value.encode()).hexdigest()
    
    def add_block(self, data):
        """Add new block to chain"""
        previous_block = self.chain[-1]
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'previous_hash': previous_block['hash'],
            'hash': self.calculate_hash(previous_block['hash'], data, datetime.now().isoformat())
        }
        self.chain.append(new_block)
        logger.info(f"🔗 Block added to blockchain: {new_block['hash'][:16]}...")
        return new_block
    
    def get_recent_blocks(self, n=10):
        """Get recent blocks"""
        return self.chain[-n:]

class NetworkMonitor:
    """Real-time network traffic monitor"""
    
    def __init__(self, model_path, interface="eth0"):
        self.model_path = model_path
        self.interface = interface
        self.model_pipeline = None
        self.packet_buffer = deque(maxlen=1000)
        self.attack_alerts = deque(maxlen=100)
        self.is_monitoring = False
        self.load_model()
        
    def load_model(self):
        """Load the trained IoT IDS model"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model_pipeline = pickle.load(f)
            logger.info(f"✅ Model loaded: {self.model_pipeline['model_type']}")
            logger.info(f"Classes: {self.model_pipeline['classes']}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def extract_features(self, packet):
        """Extract features from network packet"""
        features = {}
        
        if IP in packet:
            ip_layer = packet[IP]
            
            # Basic IP features
            features['Header_Length'] = ip_layer.ihl * 4
            features['Protocol Type'] = ip_layer.proto
            features['Duration'] = 0  # Will be calculated for flows
            features['Rate'] = 0  # Packets per second
            features['Srate'] = 0  # Source rate
            features['Drate'] = 0  # Destination rate
            
            # TCP features
            if TCP in packet:
                tcp_layer = packet[TCP]
                features['fin_flag_number'] = 1 if tcp_layer.flags.F else 0
                features['syn_flag_number'] = 1 if tcp_layer.flags.S else 0
                features['rst_flag_number'] = 1 if tcp_layer.flags.R else 0
                features['psh_flag_number'] = 1 if tcp_layer.flags.P else 0
                features['ack_flag_number'] = 1 if tcp_layer.flags.A else 0
                features['ece_flag_number'] = 1 if tcp_layer.flags.E else 0
                features['cwr_flag_number'] = 1 if tcp_layer.flags.C else 0
            else:
                # Default TCP flags to 0 for non-TCP packets
                for flag in ['fin', 'syn', 'rst', 'psh', 'ack', 'ece', 'cwr']:
                    features[f'{flag}_flag_number'] = 0
            
            # Packet size features
            features['Tot size'] = len(packet)
            features['IAT'] = 0  # Inter-arrival time
            features['Number'] = 1  # Packet count
            features['Magnitue'] = len(packet)
            features['Radius'] = 0
            features['Covariance'] = 0
            features['Variance'] = 0
            features['Weight'] = 1.0
            
            # Flow duration (simplified)
            features['flow_duration'] = 0
            
            # Add more features to match training data
            # Fill remaining features with defaults
            required_features = self.model_pipeline['feature_names']
            for feature_name in required_features:
                if feature_name not in features:
                    features[feature_name] = 0.0
        
        return features
    
    def predict_packet(self, packet_features):
        """Predict if packet is malicious"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([packet_features])
            
            # Ensure all required features are present
            for feature in self.model_pipeline['feature_names']:
                if feature not in df.columns:
                    df[feature] = 0.0
            
            # Select and order features correctly
            df = df[self.model_pipeline['feature_names']]
            
            # Scale features
            X_scaled = self.model_pipeline['scaler'].transform(df)
            
            # Predict
            prediction = self.model_pipeline['model'].predict(X_scaled)[0]
            probability = self.model_pipeline['model'].predict_proba(X_scaled)[0]
            
            # Get class name
            class_name = self.model_pipeline['label_encoder'].inverse_transform([prediction])[0]
            confidence = max(probability)
            
            return {
                'prediction': class_name,
                'confidence': confidence,
                'is_malicious': class_name != 'Benign',
                'threat_level': self.get_threat_level(class_name, confidence),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def get_threat_level(self, class_name, confidence):
        """Determine threat level"""
        if class_name == 'Benign':
            return 'None'
        
        high_threat = ['Flood Attacks', 'Botnet/Mirai Attacks', 'Backdoors & Exploits']
        medium_threat = ['Injection Attacks', 'Spoofing / MITM']
        low_threat = ['Reconnaissance']
        
        if class_name in high_threat:
            base_level = 'Critical' if confidence > 0.9 else 'High'
        elif class_name in medium_threat:
            base_level = 'Medium'
        elif class_name in low_threat:
            base_level = 'Low'
        else:
            base_level = 'Unknown'
        
        return base_level
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        try:
            # Extract features
            features = self.extract_features(packet)
            
            if features:
                # Make prediction
                result = self.predict_packet(features)
                
                if result and result['is_malicious']:
                    # Log attack
                    attack_info = {
                        'timestamp': result['timestamp'],
                        'source_ip': packet[IP].src if IP in packet else 'Unknown',
                        'dest_ip': packet[IP].dst if IP in packet else 'Unknown',
                        'attack_type': result['prediction'],
                        'threat_level': result['threat_level'],
                        'confidence': result['confidence'],
                        'packet_size': len(packet)
                    }
                    
                    self.attack_alerts.append(attack_info)
                    logger.warning(f"🚨 ATTACK DETECTED: {attack_info['attack_type']} from {attack_info['source_ip']}")
                    
                    # Add to blockchain
                    blockchain.add_block(f"Attack Detected: {attack_info['attack_type']} from {attack_info['source_ip']} at {attack_info['timestamp']}")
                
                # Store packet info
                packet_info = {
                    'timestamp': datetime.now().isoformat(),
                    'src_ip': packet[IP].src if IP in packet else 'Unknown',
                    'dst_ip': packet[IP].dst if IP in packet else 'Unknown',
                    'protocol': packet[IP].proto if IP in packet else 0,
                    'size': len(packet),
                    'prediction': result['prediction'] if result else 'Unknown',
                    'is_malicious': result['is_malicious'] if result else False
                }
                self.packet_buffer.append(packet_info)
        
        except Exception as e:
            logger.error(f"Packet handling error: {e}")
    
    def start_monitoring(self):
        """Start network monitoring"""
        self.is_monitoring = True
        logger.info(f"🔍 Starting network monitoring on {self.interface}")
        
        try:
            sniff(iface=self.interface, prn=self.packet_handler, store=0, stop_filter=lambda x: not self.is_monitoring)
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        logger.info("⏹️ Network monitoring stopped")
    
    def get_recent_attacks(self, n=10):
        """Get recent attack alerts"""
        return list(self.attack_alerts)[-n:]
    
    def get_traffic_stats(self):
        """Get traffic statistics"""
        recent_packets = list(self.packet_buffer)[-100:]  # Last 100 packets
        
        if not recent_packets:
            return {'total': 0, 'malicious': 0, 'benign': 0, 'attack_rate': 0}
        
        total = len(recent_packets)
        malicious = sum(1 for p in recent_packets if p['is_malicious'])
        benign = total - malicious
        attack_rate = (malicious / total) * 100 if total > 0 else 0
        
        return {
            'total': total,
            'malicious': malicious,
            'benign': benign,
            'attack_rate': round(attack_rate, 2)
        }

# Global instances
blockchain = BlockchainAudit()
monitor = None

# Flask Dashboard
app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    if monitor:
        stats = monitor.get_traffic_stats()
        recent_attacks = monitor.get_recent_attacks(5)
        
        return jsonify({
            'stats': stats,
            'recent_attacks': recent_attacks,
            'blockchain_blocks': len(blockchain.chain),
            'monitoring_status': monitor.is_monitoring
        })
    
    return jsonify({'error': 'Monitor not initialized'})

@app.route('/api/attacks')
def get_attacks():
    """Get recent attacks"""
    if monitor:
        attacks = monitor.get_recent_attacks(20)
        return jsonify(attacks)
    return jsonify([])

@app.route('/api/blockchain')
def get_blockchain():
    """Get recent blockchain blocks"""
    recent_blocks = blockchain.get_recent_blocks(10)
    return jsonify(recent_blocks)

@app.route('/api/traffic_chart')
def traffic_chart():
    """Generate traffic chart data"""
    if monitor:
        recent_packets = list(monitor.packet_buffer)[-50:]  # Last 50 packets
        
        timestamps = [p['timestamp'] for p in recent_packets]
        malicious_count = [1 if p['is_malicious'] else 0 for p in recent_packets]
        
        # Create cumulative counts
        cumulative_attacks = np.cumsum(malicious_count)
        
        trace = go.Scatter(
            x=timestamps,
            y=cumulative_attacks,
            mode='lines+markers',
            name='Cumulative Attacks',
            line=dict(color='red', width=2)
        )
        
        layout = go.Layout(
            title='Real-time Attack Detection',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Cumulative Attacks'),
            showlegend=True
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
    
    return jsonify({})

def main():
    """Main function"""
    global monitor
    
    print("🔒 IoT IDS Real-time Pipeline Starting...")
    print("=" * 50)
    
    # Model path - update this to your saved model
    model_path = "iot_ids_lightgbm_latest.pkl"  # Update this path
    
    try:
        # Initialize monitor
        monitor = NetworkMonitor(model_path, interface="eth0")  # Update interface
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor.start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("🚀 Network monitoring started")
        print("🌐 Starting web dashboard on http://localhost:5000")
        
        # Start Flask dashboard
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down...")
        if monitor:
            monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    main()
