"""
Network utility functions for IP filtering and validation
"""

import ipaddress
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def is_local_network_ip(ip_address: str, local_subnet: str = "192.168.100.0/24") -> bool:
    """
    Check if an IP address belongs to the local network subnet
    
    Args:
        ip_address: IP address to check
        local_subnet: Local subnet in CIDR notation (e.g., "192.168.100.0/24")
    
    Returns:
        True if IP is in local network, False otherwise
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        network = ipaddress.ip_network(local_subnet, strict=False)
        return ip in network
    except (ipaddress.AddressValueError, ValueError) as e:
        logger.warning(f"Invalid IP address or subnet: {ip_address}, {local_subnet} - {e}")
        return False

def is_internal_attack(source_ip: str, dest_ip: str, local_subnet: str = "192.168.100.0/24") -> bool:
    """
    Check if an attack is internal (both source and destination in local network)
    
    Args:
        source_ip: Source IP address
        dest_ip: Destination IP address
        local_subnet: Local subnet in CIDR notation
    
    Returns:
        True if both IPs are in local network, False otherwise
    """
    return (is_local_network_ip(source_ip, local_subnet) and 
            is_local_network_ip(dest_ip, local_subnet))

def get_local_network_ips(local_subnet: str = "192.168.100.0/24") -> List[str]:
    """
    Get all possible IP addresses in the local network
    
    Args:
        local_subnet: Local subnet in CIDR notation
    
    Returns:
        List of IP addresses in the network
    """
    try:
        network = ipaddress.ip_network(local_subnet, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        logger.error(f"Invalid subnet: {local_subnet} - {e}")
        return []

def filter_local_threats(threats: List[dict], local_subnet: str = "192.168.100.0/24", 
                        internal_only: bool = False) -> List[dict]:
    """
    Filter threats to show only local network attacks
    
    Args:
        threats: List of threat dictionaries
        local_subnet: Local subnet in CIDR notation
        internal_only: If True, only show internal attacks (both source and dest local)
    
    Returns:
        Filtered list of threats
    """
    filtered_threats = []
    
    for threat in threats:
        source_ip = threat.get('source_ip', '')
        dest_ip = threat.get('destination_ip', '')
        
        if internal_only:
            # Only internal attacks (both IPs in local network)
            if is_internal_attack(source_ip, dest_ip, local_subnet):
                filtered_threats.append(threat)
        else:
            # Any attack involving local network (source OR destination local)
            if (is_local_network_ip(source_ip, local_subnet) or 
                is_local_network_ip(dest_ip, local_subnet)):
                filtered_threats.append(threat)
    
    return filtered_threats

def get_network_info(ip_address: str) -> dict:
    """
    Get network information for an IP address
    
    Args:
        ip_address: IP address to analyze
    
    Returns:
        Dictionary with network information
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        
        info = {
            'ip': str(ip),
            'is_private': ip.is_private,
            'is_loopback': ip.is_loopback,
            'is_multicast': ip.is_multicast,
            'version': ip.version
        }
        
        # Determine network type
        if ip.is_loopback:
            info['network_type'] = 'loopback'
        elif ip.is_private:
            info['network_type'] = 'private'
        elif ip.is_multicast:
            info['network_type'] = 'multicast'
        else:
            info['network_type'] = 'public'
            
        return info
        
    except ipaddress.AddressValueError as e:
        logger.warning(f"Invalid IP address: {ip_address} - {e}")
        return {
            'ip': ip_address,
            'is_private': False,
            'is_loopback': False,
            'is_multicast': False,
            'version': None,
            'network_type': 'unknown'
        }
