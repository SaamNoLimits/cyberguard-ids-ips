"""
Blockchain Audit Service
Provides immutable audit trail for security events
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class BlockchainAudit:
    """Simple blockchain implementation for audit trail"""
    
    def __init__(self):
        self.chain = []
        self.difficulty = 4  # Number of leading zeros required in hash
        self.create_genesis_block()
        logger.info("🔗 Blockchain audit system initialized")
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'event': 'genesis_block',
                'description': 'Cybersecurity IDS/IPS Platform started',
                'system': 'audit_trail'
            },
            'previous_hash': '0',
            'nonce': 0,
            'hash': None
        }
        
        # Mine the genesis block
        genesis_block['hash'] = self._mine_block(genesis_block)
        self.chain.append(genesis_block)
        logger.info("🔗 Genesis block created")
    
    def _calculate_hash(self, block: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of block"""
        # Create string representation of block (excluding hash)
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'data': block['data'],
            'previous_hash': block['previous_hash'],
            'nonce': block['nonce']
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _mine_block(self, block: Dict[str, Any]) -> str:
        """Mine block using proof-of-work"""
        target = "0" * self.difficulty
        
        while True:
            hash_result = self._calculate_hash(block)
            
            if hash_result.startswith(target):
                logger.debug(f"Block mined with nonce: {block['nonce']}")
                return hash_result
            
            block['nonce'] += 1
            
            # Prevent infinite loop in case of issues
            if block['nonce'] > 1000000:
                logger.warning("Mining took too long, reducing difficulty")
                self.difficulty = max(1, self.difficulty - 1)
                target = "0" * self.difficulty
                block['nonce'] = 0
    
    def add_block(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new block to the chain"""
        previous_block = self.chain[-1]
        
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'previous_hash': previous_block['hash'],
            'nonce': 0,
            'hash': None
        }
        
        # Mine the new block
        new_block['hash'] = self._mine_block(new_block)
        
        # Validate block before adding
        if self._is_valid_block(new_block, previous_block):
            self.chain.append(new_block)
            logger.info(f"🔗 Block {new_block['index']} added: {new_block['hash'][:16]}...")
            return new_block
        else:
            logger.error("❌ Invalid block rejected")
            raise ValueError("Invalid block")
    
    def _is_valid_block(self, block: Dict[str, Any], previous_block: Dict[str, Any]) -> bool:
        """Validate block integrity"""
        # Check index
        if block['index'] != previous_block['index'] + 1:
            return False
        
        # Check previous hash
        if block['previous_hash'] != previous_block['hash']:
            return False
        
        # Check hash
        if block['hash'] != self._calculate_hash(block):
            return False
        
        # Check proof-of-work
        if not block['hash'].startswith("0" * self.difficulty):
            return False
        
        return True
    
    def is_chain_valid(self) -> bool:
        """Validate entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if not self._is_valid_block(current_block, previous_block):
                return False
        
        return True
    
    def get_recent_blocks(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get recent blocks from the chain"""
        return self.chain[-n:] if len(self.chain) >= n else self.chain
    
    def get_block_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_blocks_by_event_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get blocks containing specific event type"""
        matching_blocks = []
        for block in self.chain:
            if isinstance(block['data'], dict) and block['data'].get('event') == event_type:
                matching_blocks.append(block)
        return matching_blocks
    
    def search_blocks(self, search_term: str) -> List[Dict[str, Any]]:
        """Search blocks by content"""
        matching_blocks = []
        search_term_lower = search_term.lower()
        
        for block in self.chain:
            block_content = json.dumps(block['data']).lower()
            if search_term_lower in block_content:
                matching_blocks.append(block)
        
        return matching_blocks
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        if not self.chain:
            return {}
        
        # Count event types
        event_types = {}
        for block in self.chain[1:]:  # Skip genesis block
            if isinstance(block['data'], dict):
                event = block['data'].get('event', 'unknown')
                event_types[event] = event_types.get(event, 0) + 1
        
        return {
            'total_blocks': len(self.chain),
            'chain_valid': self.is_chain_valid(),
            'latest_block_hash': self.chain[-1]['hash'],
            'genesis_timestamp': self.chain[0]['timestamp'],
            'latest_timestamp': self.chain[-1]['timestamp'],
            'event_types': event_types,
            'difficulty': self.difficulty
        }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], user: str = None):
        """Log security event to blockchain"""
        audit_data = {
            'event': event_type,
            'details': details,
            'user': user,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'cybersec_ids_platform'
        }
        
        return self.add_block(audit_data)
    
    def log_user_action(self, action: str, user: str, details: Dict[str, Any] = None):
        """Log user action to blockchain"""
        audit_data = {
            'event': 'user_action',
            'action': action,
            'user': user,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.add_block(audit_data)
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system event to blockchain"""
        audit_data = {
            'event': 'system_event',
            'system_event': event,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.add_block(audit_data)
    
    def log_threat_detection(self, threat_data: Dict[str, Any]):
        """Log threat detection to blockchain"""
        audit_data = {
            'event': 'threat_detection',
            'threat_type': threat_data.get('attack_type'),
            'source_ip': threat_data.get('source_ip'),
            'destination_ip': threat_data.get('destination_ip'),
            'confidence': threat_data.get('confidence'),
            'blocked': threat_data.get('blocked', False),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.add_block(audit_data)
    
    def export_chain(self, format: str = 'json') -> str:
        """Export blockchain in specified format"""
        if format.lower() == 'json':
            return json.dumps(self.chain, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_chain(self, chain_data: str, format: str = 'json'):
        """Import blockchain from data"""
        if format.lower() == 'json':
            imported_chain = json.loads(chain_data)
            
            # Validate imported chain
            temp_blockchain = BlockchainAudit()
            temp_blockchain.chain = imported_chain
            
            if temp_blockchain.is_chain_valid():
                self.chain = imported_chain
                logger.info(f"✅ Blockchain imported successfully ({len(self.chain)} blocks)")
            else:
                raise ValueError("Invalid blockchain data")
        else:
            raise ValueError(f"Unsupported import format: {format}")
