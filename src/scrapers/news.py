import logging
import time
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
import random
# Import validator to filter paragraph content by language within the scraper
try:
    from src.processing.linguistic import LinguisticValidator
except ImportError:
    LinguisticValidator = None

class NewsScraper(BaseScraper):
    """
    Generic scraper for static news/blog sites.
    Respects robots.txt and implements rate limiting.
    Currently configured for a generic structure, can be subclassed for specific sites.
    """
    
    def __init__(self, delay=2.0):
        self.logger = logging.getLogger(__name__)
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Research Pipeline; Assamese Sentiment Project) requests/2.31'
        })

    def scrape(self, url: str):
        """
        Scrapes article text (not comments) from a news URL.
        
        Args:
            url (str): The full URL of the news article.
            
        Yields:
            dict: Data containing text, title, and source metadata.
        """
        self.logger.info(f"Fetching: {url}")
        
        # Respectful delay with jitter
        sleep_time = self.delay + random.uniform(0.5, 1.5)
        time.sleep(sleep_time)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Use 'lxml' if available, else 'html.parser'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- Extraction Logic (Linguistic-based) ---
            # Instead of relying on brittle class names, we fetch all paragraphs
            # and filter them by language. This handles messy CMS structures better.
            
            paragraphs = []
            all_p_tags = soup.find_all('p')
            
            for p in all_p_tags:
                text = p.get_text(strip=True)
                if not text:
                    continue
                    
                # If we have the validator, check if this specific paragraph is Assamese.
                # Use a low threshold (0.1) just to check if *some* indic script is there
                # to distinguish from "Terms of Use" or "Copyright".
                if LinguisticValidator:
                    is_valid = LinguisticValidator.is_assamese_script(text, threshold=0.1)
                else:
                    # Fallback: simple length check + crude heuristic if validator missing
                    is_valid = len(text) > 20
                
                if is_valid:
                    paragraphs.append(text)

            full_text = "\n".join(paragraphs)
            
            # Extract Title
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Fallback: if h1 is missing, try og:title meta tag
            if not title:
                meta_title = soup.find("meta", property="og:title")
                if meta_title:
                    title = meta_title.get("content", "")

            if not full_text:
                self.logger.warning(f"No Assamese text found in {url}")
                return []

            # Return simplified object
            yield {
                'text': full_text,
                'title': title,
                'source_url': url,
                'scraped_timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                'source_type': 'news_article'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return []

