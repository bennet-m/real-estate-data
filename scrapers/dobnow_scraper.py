from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper


class DOBNOWScraper(BaseScraper):
    """Scraper for DOBNOW website to extract building data"""
    
    def _scrape_flood_hazard_check(self, driver):
        """Scrape Special Flood Hazard Area Check from the page"""
        print("🌊 Scraping Special Flood Hazard Area Check...")
        
        building_data = {}
        wait = WebDriverWait(driver, 20)  # Increased timeout for slow loading
        
        try:
            # Wait for the page to load and find the Special Flood Hazard Area Check
            # The structure is: two divs - one with the label, one with the value
            # Label div: <div class="col-xs-8 col-sm-6 col-md-4 col-lg-4 top-pad-5"><strong>Special Flood Hazard Area Check:    </strong></div>
            # Value div: <div class="col-xs-4 col-sm-6 col-md-8 col-lg-8 top-pad-5 ng-binding">No</div>
            
            print("  ⏳ Waiting for Special Flood Hazard Area Check element...")
            
            # Method 1: Find the label div, then find the next sibling value div
            try:
                # Find the div containing the label
                label_div_xpath = "//div[contains(@class, 'col-xs-8') and contains(@class, 'col-sm-6') and contains(@class, 'col-md-4') and contains(@class, 'col-lg-4') and contains(@class, 'top-pad-5')]//strong[contains(text(), 'Special Flood Hazard Area Check')]/ancestor::div[contains(@class, 'col-xs-8')]"
                
                label_div = wait.until(EC.presence_of_element_located((By.XPATH, label_div_xpath)))
                print("  ✅ Found Special Flood Hazard Area Check label div")
                
                # Find the next sibling div that contains the value
                # The value div should be the next sibling with the specific classes
                value_div_xpath = "./following-sibling::div[contains(@class, 'col-xs-4') and contains(@class, 'col-sm-6') and contains(@class, 'col-md-8') and contains(@class, 'col-lg-8') and contains(@class, 'top-pad-5') and contains(@class, 'ng-binding')]"
                
                value_element = label_div.find_element(By.XPATH, value_div_xpath)
                flood_hazard_value = self.get_element_text(value_element)
                
                if flood_hazard_value:
                    building_data["Special Flood Hazard Area Check"] = flood_hazard_value
                    print(f"  📊 Special Flood Hazard Area Check: {flood_hazard_value}")
                    return building_data
                else:
                    print("  ⚠️ Could not extract Special Flood Hazard Area Check value")
            except Exception as e1:
                print(f"  ⚠️ Method 1 failed: {str(e1)}")
                raise  # Re-raise to try alternative method
                
        except Exception as e:
            print(f"  ⚠️ Error extracting Special Flood Hazard Area Check: {str(e)}")
            # Try alternative approach - search for the text directly and find nearby value
            try:
                print("  🔄 Trying alternative extraction method...")
                # Alternative: Find the strong element, then find the value div in the same row
                alt_xpath = "//strong[contains(text(), 'Special Flood Hazard Area Check')]/ancestor::div[contains(@class, 'row') or contains(@class, 'col-')]//div[contains(@class, 'ng-binding') and contains(@class, 'top-pad-5')]"
                value_element = wait.until(EC.presence_of_element_located((By.XPATH, alt_xpath)))
                flood_hazard_value = self.get_element_text(value_element)
                if flood_hazard_value:
                    building_data["Special Flood Hazard Area Check"] = flood_hazard_value
                    print(f"  📊 Special Flood Hazard Area Check (alternative method): {flood_hazard_value}")
            except Exception as e2:
                print(f"  ⚠️ Alternative extraction method also failed: {str(e2)}")
                # Last resort: try to find any div with ng-binding that follows the label
                try:
                    print("  🔄 Trying last resort extraction method...")
                    last_resort_xpath = "//strong[contains(text(), 'Special Flood Hazard Area Check')]/ancestor::div[1]/following-sibling::div[contains(@class, 'ng-binding')]"
                    value_element = wait.until(EC.presence_of_element_located((By.XPATH, last_resort_xpath)))
                    flood_hazard_value = self.get_element_text(value_element)
                    if flood_hazard_value:
                        building_data["Special Flood Hazard Area Check"] = flood_hazard_value
                        print(f"  📊 Special Flood Hazard Area Check (last resort method): {flood_hazard_value}")
                except Exception as e3:
                    print(f"  ⚠️ All extraction methods failed: {str(e3)}")
        
        return building_data
    
    def _scrape_data(self, driver, wait):
        """Scrape building data from DOBNOW page"""
        # Wait for page to load by checking for body element
        print("  ⏳ Waiting for page to load...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Wait a bit more for dynamic content to start loading (Angular apps need time)
        time.sleep(3)
        
        # Wait for Angular to finish loading (check for ng-binding class or other Angular indicators)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ng-binding, [ng-binding]")))
            print("  ✅ Angular content detected")
        except Exception:
            print("  ⚠️ Angular content not detected, continuing anyway...")
        
        # Additional wait for dynamic content
        time.sleep(2)
        
        # Scrape flood hazard information
        building_data = self._scrape_flood_hazard_check(driver)
        
        return building_data

