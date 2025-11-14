from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod
import time
import traceback


class BaseScraper(ABC):
    """Base class for all scrapers with common functionality"""
    
    def __init__(self):
        pass
    
    def get_element_text(self, element):
        """Extract text from element using multiple methods for robustness"""
        # Try different text extraction methods in order of preference
        text = element.text or element.get_attribute('textContent') or element.get_attribute('innerText')
        return text.strip() if text else ""
    
    def _setup_driver(self):
        """Setup Chrome driver with proper configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size to ensure content loads
        chrome_options.add_argument("--start-maximized")  # Start maximized
        chrome_options.add_argument("--disable-web-security")  # Disable web security for better compatibility
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # Disable compositor for stability
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Ensure window is properly sized for content loading
        driver.set_window_size(1920, 1080)
        driver.maximize_window()
        
        return driver, wait
    
    @abstractmethod
    def _scrape_data(self, driver, wait):
        """Abstract method to be implemented by subclasses for specific scraping logic"""
        pass
    
    def scrape_building_data(self, url):
        """Main method to scrape building data from the given URL"""
        driver, wait = self._setup_driver()
        
        try:
            print(f"🌐 Navigating to URL: {url}")
            driver.get(url)
            
            # Call the abstract method implemented by subclasses
            building_data = self._scrape_data(driver, wait)
            
            # Return the scraped data
            return building_data
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Full error traceback:\n{error_details}")
            scraper_name = self.__class__.__name__
            raise Exception(f"Error scraping {scraper_name} data: {str(e)}\nFull traceback: {error_details}")
        finally:
            driver.quit()

