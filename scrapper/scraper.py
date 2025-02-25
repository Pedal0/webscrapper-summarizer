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
            items.append({'text': p.get_text(strip=True)})
        return items

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

class Thema:
    def __init__(self, name: str, keywords: List[str]):
        self.name = name
        self.keywords = keywords

def scrape_the_web(selected_theme: str) -> List[Dict]:
    theme_url_mapping = {
        "Actualité": "https://www.bbc.com/news",
        "Technologie": "https://techcrunch.com",
        "Science": "https://www.sciencesetavenir.fr/"
    }
    url = theme_url_mapping.get(selected_theme, "https://www.example.com")
    theme_instance = Thema(selected_theme, [])
    scraper = WebScraper(theme_instance)
    return scraper.scrap(url)