import validators
import re
from urllib.parse import urlparse

class URLValidator:
    # Lista de dominios maliciosos conocidos (básica)
    BLACKLISTED_DOMAINS = [
        'bit.ly/malware',
        'phishing-site.com',
        'malware-download.net',
        'fake-bank.com',
        'scam-site.org'
    ]
    
    # Patrones sospechosos en URLs
    SUSPICIOUS_PATTERNS = [
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
        r'@',  # @ symbol (often used in phishing)
        r'%[0-9a-fA-F]{2}',  # Encoded characters
        r'\-{3,}',  # Multiple dashes
        r'[a-z]{30,}',  # Very long strings
    ]
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Valida si es una URL bien formada"""
        return validators.url(url) is True
    
    @staticmethod
    def check_blacklist(url: str) -> dict:
        """Verifica si la URL está en lista negra"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for blacklisted in URLValidator.BLACKLISTED_DOMAINS:
            if blacklisted.lower() in domain or blacklisted.lower() in url.lower():
                return {
                    'is_blacklisted': True,
                    'reason': f'Domain matches blacklist entry: {blacklisted}'
                }
        
        return {'is_blacklisted': False, 'reason': None}
    
    @staticmethod
    def check_suspicious_patterns(url: str) -> dict:
        """Detecta patrones sospechosos en la URL"""
        suspicious_findings = []
        
        # Check for IP address instead of domain
        if re.search(URLValidator.SUSPICIOUS_PATTERNS[0], url):
            suspicious_findings.append('URL uses IP address instead of domain name')
        
        # Check for @ symbol
        if '@' in url:
            suspicious_findings.append('URL contains @ symbol (potential phishing)')
        
        # Check for excessive URL encoding
        encoded_chars = re.findall(URLValidator.SUSPICIOUS_PATTERNS[2], url)
        if len(encoded_chars) > 5:
            suspicious_findings.append('URL contains excessive encoded characters')
        
        # Check for multiple consecutive dashes
        if re.search(URLValidator.SUSPICIOUS_PATTERNS[3], url):
            suspicious_findings.append('URL contains unusual dash patterns')
        
        # Check for suspiciously long strings
        if re.search(URLValidator.SUSPICIOUS_PATTERNS[4], url):
            suspicious_findings.append('URL contains unusually long string sequences')
        
        return {
            'has_suspicious_patterns': len(suspicious_findings) > 0,
            'findings': suspicious_findings,
            'risk_score': min(len(suspicious_findings) * 20, 100)
        }
    
    @staticmethod
    def analyze_url_structure(url: str) -> dict:
        """Analiza la estructura de la URL"""
        parsed = urlparse(url)
        
        return {
            'protocol': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'has_https': parsed.scheme == 'https',
            'subdomain_count': len(parsed.netloc.split('.')) - 2 if len(parsed.netloc.split('.')) > 2 else 0,
            'path_depth': len([p for p in parsed.path.split('/') if p]),
        }