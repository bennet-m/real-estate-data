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

    def scrape_building_data(self, building_id):
        """Scrape building data using a BIN (Building Identification Number).
        
        Navigates to the DOBNOW search page, clicks the BIN search button,
        enters the building ID, and performs the search.
        
        Args:
            building_id: The BIN to search for (7-digit number)
        """
        try:    
            # Normalize input
            input_str = str(building_id).strip()
            
            # Start with the search page
            search_url = "https://a810-dobnow.nyc.gov/publish/Index.html#!/search"
            print(f"🌐 Navigating to DOBNOW search page: {search_url}")
            
            # Use the base class setup to create driver and navigate
            driver, wait = self._setup_driver()
            
            # Navigate to the search page
            driver.get(search_url)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            # Click the BIN search button
            print("🔘 Clicking BIN search button...")
            bin_button_xpath = "//button[@role='img' and @aria-label='Search by BIN']"
            bin_button = wait.until(EC.element_to_be_clickable((By.XPATH, bin_button_xpath)))
            bin_button.click()
            print("waiting")
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            print("ready")
            time.sleep(4)
            
            # Enter the building ID in the input field
            print(f"⌨️  Entering BIN: {input_str}")
            bin_input = wait.until(EC.presence_of_element_located((By.ID, "enterbin")))
            # bin_input = wait.until(
            #     EC.element_to_be_clickable((By.ID, "enterbin"))
            # )
            # print('waited')
            bin_input = driver.find_element(By.ID, "enterbin")

            bin_input = driver.find_element(By.ID, "enterbin")

            # Use JavaScript to set the value AND trigger Angular input event
            driver.execute_script("""
            var input = arguments[0];
            var value = arguments[1];
            input.focus();
            input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            """, bin_input, input_str)

            # time.sleep(300)
            # driver.execute_script("arguments[0].focus();", bin_input)
            # print('focuised')
            # bin_input.click()
            # print('clicked')
            # bin_input.send_keys(input_str)
            
            # Click the search button
            print("🔍 Clicking search button...")
            time.sleep(2)
            search_btn = driver.find_element(By.ID, "search2")
            driver.execute_script("arguments[0].click();", search_btn)
            
            # Wait for results to load
            print("⏳ Waiting for search results...")
            time.sleep(3) 
            
            # Scrape the data from the results page
            data = self._scrape_data(driver, wait)
            
            return data
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Full error traceback:\n{error_details}")
            raise Exception(f"Error scraping {e} data: {str(e)}\nFull traceback: {error_details}")

