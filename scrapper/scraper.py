import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, theme, max_retries=3, timeout=10):
        self.theme = theme
        self.max_retries = max_retries
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    
    def _make_request(self, url: str) -> str:
        headers = {"User-Agent": self.user_agent}
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()  
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Impossible de récupérer la page {url} après {self.max_retries} tentatives. Erreur: {e}")
                    raise
                logger.warning(f"Erreur lors de la récupération de {url} (Tentative {attempt+1}/{self.max_retries}). Nouvel essai dans 1 seconde.")
                time.sleep(1)
        return ""

    def _parse_html(self, html: str, base_url: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  
                items.append({'type': 'paragraph', 'text': text})
        
        for i in range(1, 4):
            for h in soup.find_all(f'h{i}'):
                items.append({'type': f'heading{i}', 'text': h.get_text(strip=True)})
        
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if text and len(text) > 10:
                items.append({'type': 'listitem', 'text': text})
                
        for article in soup.find_all('article'):
            items.append({'type': 'article', 'text': article.get_text(strip=True)})
        
        return items

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                full_url = base_url + href
                links.append(full_url)
            elif href.startswith(('http://', 'https://')) and base_url in href:
                links.append(href)
        return links

    def scrap(self, url: str) -> List[Dict]:
        logger.info(f"Démarrage du scraping de {url}")
        try:
            html = self._make_request(url)
            if not html:
                logger.warning(f"Aucun contenu récupéré pour {url}")
                return []
            items = self._parse_html(html, url)
            logger.info(f"Nombre d'éléments extraits : {len(items)}")
            return items
        except Exception as e:
            logger.error(f"Erreur pendant le scraping de {url}: {e}")
            return []

    def scrap_with_depth(self, url: str, depth: int = 1) -> List[Dict]:
        """Scrape URL and follow links up to specified depth"""
        if depth <= 0:
            return []
            
        base_url = '/'.join(url.split('/')[:3])
        items = self.scrap(url)
        
        if depth > 1:
            html = self._make_request(url)
            soup = BeautifulSoup(html, 'html.parser')
            links = self._extract_links(soup, base_url)
            
            for link in links[:3]: 
                items.extend(self.scrap_with_depth(link, depth - 1))
                time.sleep(1) 
                
        return items

class Thema:
    def __init__(self, name: str, keywords: List[str]):
        self.name = name
        self.keywords = keywords

def scrape_the_web(selected_theme: str, depth: int = 1) -> List[Dict]:
    theme_url_mapping = {
        "Actualité": [
            "https://www.bbc.com/news",
            "https://www.reuters.com",
            "https://www.lemonde.fr"
        ],
        "Technologie": [
            "https://techcrunch.com",
            "https://www.theverge.com",
            "https://www.wired.com"
        ],
        "Science": [
            "https://www.sciencesetavenir.fr/",
            "https://www.sciencemag.org",
            "https://www.nature.com"
        ]
    }
    
    all_scraped_data = []
    urls = theme_url_mapping.get(selected_theme, ["https://www.example.com"])
    theme_instance = Thema(selected_theme, [])
    scraper = WebScraper(theme_instance)
    
    for url in urls:
        # Utiliser scrap_with_depth au lieu de scrap
        all_scraped_data.extend(scraper.scrap_with_depth(url, depth))
        
    return all_scraped_data