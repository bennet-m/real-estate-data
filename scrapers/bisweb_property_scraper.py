from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper


class BISWEBPropertyScraper(BaseScraper):
    """Scraper for BISWEB Property Profile Overview page to extract landmark status, additional BINs, and violations"""
    
    def scrape_building_data(self, borough=None, block=None, lot=None, url=None):
        """Main entry: navigate by borough/block/lot form or by URL, then scrape."""
        driver, _ = self._setup_driver()

        try:
            if borough and block and lot:
                print("🌐 Navigating to BISWEB Property Info portal (by BBL)...")
                driver.get(
                    f"https://a810-bisweb.nyc.gov/bisweb/PropertyProfileOverviewServlet?"
                    f"boro={borough}&block={block}&lot={lot}&go3=+GO+&requestid={0}"
                )
            elif url:
                print(f"🌐 Navigating to URL: {url}")
                driver.get(url)
            else:
                raise ValueError("Either (borough, block, lot) or url must be provided")

            # Call the subclass scraping implementation
            building_data = self._scrape_data(driver, WebDriverWait(driver, 10))

            return building_data
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Full error traceback:\n{error_details}")
            scraper_name = self.__class__.__name__
            raise Exception(f"Error scraping {scraper_name} data: {str(e)}\nFull traceback: {error_details}")
        finally:
            driver.quit()

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
                    print("  📊 Additional BINs: NONE")
        except Exception as e:
            print(f"  ⚠️ Error extracting Additional BINs: {str(e)}")
        
        # Scrape DOB Violations
        try:
            print("  ⏳ Looking for DOB Violations row...")
            # Find the row containing "Violations-DOB" link
            dob_violations_row = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//tr[td[@class='content']//a[contains(@href, 'ActionsByLocationServlet') and contains(., 'Violations-DOB')]]")
                )
            )
            
            # Get all cells in this row
            cells = dob_violations_row.find_elements(By.CSS_SELECTOR, "td.content")
            
            # Second cell (index 1) is total, third cell (index 2) is open
            if len(cells) >= 3:
                total_dob = self.get_element_text(cells[1])
                open_dob = self.get_element_text(cells[2])
                
                if total_dob:
                    building_data["DOB Violations Total"] = total_dob
                    print(f"  📊 DOB Violations Total: {total_dob}")
                if open_dob:
                    building_data["DOB Violations Open"] = open_dob
                    print(f"  📊 DOB Violations Open: {open_dob}")
        except Exception as e:
            print(f"  ⚠️ Error extracting DOB Violations: {str(e)}")
        
        # Scrape ECB Violations
        try:
            print("  ⏳ Looking for ECB Violations row...")
            # Find the row containing "Violations-OATH/ECB" link
            ecb_violations_row = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//tr[td[@class='content']//a[contains(@href, 'ECBQueryByLocationServlet') and contains(., 'Violations-OATH/ECB')]]")
                )
            )
            
            # Get all cells in this row
            cells = ecb_violations_row.find_elements(By.CSS_SELECTOR, "td.content")
            
            # Second cell (index 1) is total, third cell (index 2) is open
            if len(cells) >= 3:
                total_ecb = self.get_element_text(cells[1])
                open_ecb = self.get_element_text(cells[2])
                
                if total_ecb:
                    building_data["ECB Violations Total"] = total_ecb
                    print(f"  📊 ECB Violations Total: {total_ecb}")
                if open_ecb:
                    building_data["ECB Violations Open"] = open_ecb
                    print(f"  📊 ECB Violations Open: {open_ecb}")
        except Exception as e:
            print(f"  ⚠️ Error extracting ECB Violations: {str(e)}")
        
        return building_data

