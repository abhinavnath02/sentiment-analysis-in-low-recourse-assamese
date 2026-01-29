from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    Abstract base class for all scraper implementations.
    Enforces a common interface for the pipeline.
    """
    
    @abstractmethod
    def scrape(self, target: str):
        """
        Scrapes data from the target (URL, ID, etc.)
        
        Args:
            target (str): The identifier for the resource to scrape.
            
        Returns:
            Generator or List of dictionaries containing raw scraped data.
        """
        pass
