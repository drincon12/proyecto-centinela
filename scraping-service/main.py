import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ScrapingService:
    """Servicio de web scraping para análisis de contenido"""
    
    @staticmethod
    async def scrape_url(url: str) -> dict:
        """Extrae contenido y metadata de una URL"""
        try:
            logger.info(f"Starting scraping for URL: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información
            title = ScrapingService._extract_title(soup)
            description = ScrapingService._extract_description(soup)
            text_content = ScrapingService._extract_text_content(soup)
            links = ScrapingService._extract_links(soup, url)
            images = ScrapingService._extract_images(soup)
            
            result = {
                'url': url,
                'status': 'success',
                'title': title,
                'description': description,
                'text_content': text_content[:1000],  # Limitar a 1000 caracteres
                'text_length': len(text_content),
                'links_count': len(links),
                'external_links': ScrapingService._count_external_links(links, url),
                'images_count': len(images),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scraping completed for {url}")
            return result
            
        except requests.Timeout:
            logger.error(f"Timeout scraping {url}")
            return {
                'url': url,
                'status': 'error',
                'error': 'Timeout - site took too long to respond',
                'scraped_at': datetime.utcnow().isoformat()
            }
        except requests.RequestException as e:
            logger.error(f"Request error scraping {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': f'Request error: {str(e)}',
                'scraped_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'scraped_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        """Extrae el título de la página"""
        if soup.title:
            return soup.title.string.strip() if soup.title.string else 'No title'
        
        # Try og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        return 'No title found'
    
    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str:
        """Extrae la descripción de la página"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return 'No description found'
    
    @staticmethod
    def _extract_text_content(soup: BeautifulSoup) -> str:
        """Extrae el contenido de texto de la página"""
        # Remover scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Obtener texto
        text = soup.get_text()
        
        # Limpiar espacios en blanco
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    @staticmethod
    def _extract_links(soup: BeautifulSoup, base_url: str) -> list:
        """Extrae todos los enlaces de la página"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                links.append(href)
        return links
    
    @staticmethod
    def _extract_images(soup: BeautifulSoup) -> list:
        """Extrae todas las imágenes de la página"""
        images = []
        for img in soup.find_all('img', src=True):
            images.append(img['src'])
        return images
    
    @staticmethod
    def _count_external_links(links: list, base_url: str) -> int:
        """Cuenta cuántos enlaces son externos"""
        from urllib.parse import urlparse
        base_domain = urlparse(base_url).netloc
        
        external_count = 0
        for link in links:
            link_domain = urlparse(link).netloc
            if link_domain and link_domain != base_domain:
                external_count += 1
        
        return external_count