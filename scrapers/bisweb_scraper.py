from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class BISWEBScraper:
    """Scraper for BISWEB website to extract building data"""
    
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
    
    def _scrape_building_info(self, driver):
        """Scrape building information from the BISWEB page"""
        print("🏢 Scraping BISWEB building information...")
        
        building_data = {}
        wait = WebDriverWait(driver, 20)  # Increased timeout for slow loading
        
        try:
            print("  ⏳ Waiting for Building Information card to load...")
            # Find the card with "Building Information" text
            building_info_card = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'card')]//p[contains(text(), 'Building Information')]/ancestor::div[contains(@class, 'card')]")))
            print("  ✅ Building Information card loaded")
            
            # Wait a bit for nested content to populate
            time.sleep(1)
            
            # Find all label-value pairs in the card
            # Each pair is in a div with class "sc-kdBSHD gjouCV"
            # Value is in p.sc-hRJfrW.jVlUZz, label is in p.sc-cfxfcM.eyvGek
            info_sections = building_info_card.find_elements(By.CSS_SELECTOR, ".sc-gFAWRd.evnkkT")
            valid_labels = ["Residential Units", "Commercial Units", "Commercial Area", "Year Built", "Stories"]
            for section in info_sections:
                info_items = section.find_elements(By.CSS_SELECTOR, ".sc-kdBSHD.gjouCV")
                for item in info_items:
                    try:
                        label_elem = item.find_element(By.CSS_SELECTOR, "p.sc-cfxfcM.eyvGek")
                        value_elem = item.find_element(By.CSS_SELECTOR, "p.sc-hRJfrW.jVlUZz")
                        
                        label = self.get_element_text(label_elem)
                        value = self.get_element_text(value_elem)
                        
                        if label and value:
                            if label in valid_labels:
                                building_data[label] = value
                                print(f"  📊 {label}: {value}")
                            else:
                                print(f"  ⚠️ Not collecting label: {label}")
                    except Exception:
                        continue  # Skip items that don't have the expected structure
            
        except Exception as e:
            print(f"  ⚠️ Error extracting Building Information card data: {str(e)}")
                    
        # Extract Building Type
        try:
            print("  ⏳ Waiting for Building Type element...")
            building_type_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.sc-hRJfrW.jVlUZz")))
            building_type = self.get_element_text(building_type_element)
            if building_type:
                building_data["Building Type"] = building_type
                print(f"  📊 Building Type: {building_type}")
        except Exception as e:
            print(f"  ⚠️ Error extracting Building Type: {str(e)}")
        
        # Extract Total Value and Taxable Billable AV from the table with thead.table-primary
        try:
            print("  ⏳ Waiting for table to load...")
            # Wait for table header to be visible
            table_header = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "thead.table-primary")))
            
            # Wait a bit for table content to populate
            time.sleep(1)
            
            # Find the table with thead.table-primary
            table = table_header.find_element(By.XPATH, "./..")
            
            # Wait for table rows to be present
            print("  ⏳ Waiting for table rows...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr")))
            
            # Find the first data row (tbody tr or table tr after thead)
            try:
                # Try to find tbody first
                tbody = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody")))
                wait.until(lambda d: len(tbody.find_elements(By.CSS_SELECTOR, "tr")) > 0)
                first_row = tbody.find_element(By.CSS_SELECTOR, "tr")
            except Exception:
                # If no tbody, find first tr after thead
                wait.until(lambda d: len(table.find_elements(By.CSS_SELECTOR, "tr")) > 1)
                all_rows = table.find_elements(By.CSS_SELECTOR, "tr")
                # Skip the header row (thead tr)
                if len(all_rows) > 1:
                    first_row = all_rows[1]
                else:
                    raise Exception("No data rows found in table")
            
            # Wait for cells to be present
            wait.until(lambda d: len(first_row.find_elements(By.CSS_SELECTOR, "td, th")) >= 8)
            
            # Get all cells from the first row
            cells = first_row.find_elements(By.CSS_SELECTOR, "td, th")
            
            # Based on the thead structure: FY, Building Class, Tax Class, Land Value, Improvement Value, Total Value, Change, Taxable Billable AV, Change
            # We want Building Class (index 1), Tax Class (index 2), Total Value (index 5) and Taxable Billable AV (index 7)
            if len(cells) >= 8:
                building_class = self.get_element_text(cells[1])
                tax_class = self.get_element_text(cells[2])
                total_value = self.get_element_text(cells[5])
                taxable_value = self.get_element_text(cells[7])
                
                if building_class:
                    building_data["Building Class"] = building_class
                    print(f"  📊 Building Class: {building_class}")
                if tax_class:
                    building_data["Tax Class"] = tax_class
                    print(f"  📊 Tax Class: {tax_class}")
                if total_value:
                    building_data["Total Value"] = total_value
                    print(f"  📊 Total Value: {total_value}")
                if taxable_value:
                    building_data["Taxable Billable AV"] = taxable_value
                    print(f"  📊 Taxable Billable AV: {taxable_value}")
            else:
                print(f"  ⚠️ Table row doesn't have enough columns (found {len(cells)}, expected at least 8)")
                
        except Exception as e:
            print(f"  ⚠️ Error extracting table data (Building Class, Tax Class, Total Value, Taxable Billable AV): {str(e)}")
            
        
        return building_data
    
    def scrape_building_data(self, url):
        """Main method to scrape building data from the given BISWEB URL"""
        driver, wait = self._setup_driver()
        
        try:
            print(f"🌐 Navigating to BISWEB URL: {url}")
            driver.get(url)
            
            # Wait for page to be in ready state
            print("  ⏳ Waiting for page to load...")
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # Wait a bit more for dynamic content to start loading
            time.sleep(2)
            
            # Scrape building information
            building_data = self._scrape_building_info(driver)
            
            # Return the scraped data
            return building_data

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Full error traceback:\n{error_details}")
            raise Exception(f"Error scraping BISWEB data: {str(e)}\nFull traceback: {error_details}")
        finally:
            driver.quit()
