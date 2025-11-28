import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from ..utils.url_validator import URLValidator
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.url_validator import URLValidator

logger = logging.getLogger(__name__)

class URLAnalysisService:
    """Servicio de análisis de seguridad de URLs"""
    
    @staticmethod
    async def analyze_url(url: str) -> dict:
        """Análisis completo de seguridad de una URL"""
        try:
            logger.info(f"Starting analysis for URL: {url}")
            
            # Validación básica
            if not URLValidator.is_valid_url(url):
                return {
                    'url': url,
                    'status': 'invalid',
                    'threat_level': 'unknown',
                    'error': 'Invalid URL format',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Análisis de estructura
            structure_analysis = URLValidator.analyze_url_structure(url)
            
            # Verificación de lista negra
            blacklist_check = URLValidator.check_blacklist(url)
            
            # Verificación de patrones sospechosos
            pattern_check = URLValidator.check_suspicious_patterns(url)
            
            # Cálculo de nivel de amenaza
            threat_level = URLAnalysisService._calculate_threat_level(
                blacklist_check,
                pattern_check,
                structure_analysis
            )
            
            # Intentar obtener información del sitio
            site_info = await URLAnalysisService._get_site_info(url)
            
            analysis_result = {
                'url': url,
                'status': 'analyzed',
                'threat_level': threat_level,
                'structure': structure_analysis,
                'blacklist': blacklist_check,
                'patterns': pattern_check,
                'site_info': site_info,
                'timestamp': datetime.utcnow().isoformat(),
                'recommendations': URLAnalysisService._generate_recommendations(
                    threat_level,
                    blacklist_check,
                    pattern_check
                )
            }
            
            logger.info(f"Analysis completed for {url}: {threat_level}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'threat_level': 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def _get_site_info(url: str) -> dict:
        """Obtiene información básica del sitio web"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            return {
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'redirected': len(response.history) > 0,
                'final_url': response.url if len(response.history) > 0 else url,
                'content_type': response.headers.get('content-type', 'unknown'),
                'server': response.headers.get('server', 'unknown')
            }
        except requests.Timeout:
            return {'accessible': False, 'error': 'Timeout - site took too long to respond'}
        except requests.ConnectionError:
            return {'accessible': False, 'error': 'Connection error - site may be down'}
        except Exception as e:
            return {'accessible': False, 'error': f'Error accessing site: {str(e)}'}
    
    @staticmethod
    def _calculate_threat_level(blacklist: dict, patterns: dict, structure: dict) -> str:
        """Calcula el nivel de amenaza basado en múltiples factores"""
        risk_score = 0
        
        # Lista negra es el indicador más fuerte
        if blacklist.get('is_blacklisted'):
            return 'high'
        
        # Agregar score por patrones sospechosos
        risk_score += patterns.get('risk_score', 0)
        
        # Penalizar falta de HTTPS
        if not structure.get('has_https'):
            risk_score += 20
        
        # Penalizar múltiples subdominios
        if structure.get('subdomain_count', 0) > 2:
            risk_score += 15
        
        # Calcular nivel de amenaza
        if risk_score >= 60:
            return 'high'
        elif risk_score >= 30:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _generate_recommendations(threat_level: str, blacklist: dict, patterns: dict) -> list:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        if threat_level == 'high':
            recommendations.append('⚠️ DO NOT visit this URL - High risk detected')
            if blacklist.get('is_blacklisted'):
                recommendations.append('🚨 URL is in known malicious domains list')
        
        if threat_level == 'medium':
            recommendations.append('⚡ Exercise caution - Suspicious patterns detected')
            recommendations.append('Consider using a sandbox environment')
        
        if patterns.get('has_suspicious_patterns'):
            for finding in patterns.get('findings', []):
                recommendations.append(f'⚠️ {finding}')
        
        if threat_level == 'low':
            recommendations.append('✅ No major threats detected')
            recommendations.append('Always verify the source before sharing sensitive information')
        
        return recommendations
