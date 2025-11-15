from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper


class BISWEBPropertyScraper(BaseScraper):
    """Scraper for BISWEB Property Profile Overview page to extract landmark status and additional BINs"""
    
    def _scrape_data(self, driver, wait):
        """Scrape building data from BISWEB Property Profile Overview page"""
        print("🏢 Scraping BISWEB Property Profile Overview data...")
        
        # Wait for page to be in ready state
        print("  ⏳ Waiting for page to load...")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # Wait a bit more for dynamic content to start loading
        time.sleep(2)
        
        building_data = {}
        
        # Scrape Landmark Status
        try:
            print("  ⏳ Looking for Landmark Status row...")
            # Find the row containing "Landmark Status:"
            landmark_row = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//tr[td[@class='content' and contains(., 'Landmark Status:')]]")
                )
            )
            
            # Get all cells in this row
            cells = landmark_row.find_elements(By.CSS_SELECTOR, "td.content")
            
            # The landmark status value should be in the second cell (index 1)
            if len(cells) >= 2:
                landmark_status = self.get_element_text(cells[1])
                if landmark_status:
                    building_data["Landmark Status"] = landmark_status
                    print(f"  📊 Landmark Status: {landmark_status}")
        except Exception as e:
            print(f"  ⚠️ Error extracting Landmark Status: {str(e)}")
        
        # Scrape Additional BINs
        try:
            print("  ⏳ Looking for Additional BINs row...")
            # Find the row containing "Additional BINs for Building:"
            bins_row = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//tr[td[@class='content' and contains(., 'Additional BINs for Building:')]]")
                )
            )
            
            # Get all cells in this row
            cells = bins_row.find_elements(By.CSS_SELECTOR, "td.content")
            
            # The additional BINs value should be in the second cell (index 1)
            if len(cells) >= 2:
                bins_text = self.get_element_text(cells[1])
                
                # Clean up the text - remove any extra whitespace and newlines
                bins_text = ' '.join(bins_text.split())
                
                if bins_text and bins_text.upper() != "NONE":
                    building_data["Additional BINs"] = bins_text
                    print(f"  📊 Additional BINs: {bins_text}")
                else:
                    building_data["Additional BINs"] = "NONE"
                    print(f"  📊 Additional BINs: NONE")
        except Exception as e:
            print(f"  ⚠️ Error extracting Additional BINs: {str(e)}")
        
        return building_data

