from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class HPDScraper:
    """Scraper for HPD Online website to extract building data"""
    
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
    
    def _scrape_violations(self, driver):
        """Scrape violation data from the page"""
        print("🔍 Scraping violation data...")
        violations = {}
        violation_types = ["A", "B", "C", "I"]
        
        for vtype in violation_types:
            try:
                element = driver.find_element(By.XPATH, f"//span[contains(normalize-space(.),'{vtype} Class')]/span[@class='fw-bold']")
                text = self.get_element_text(element)
                if text:
                    print(f"  {vtype} Class violations: '{text}'")
                    violations[vtype] = int(text)
            except Exception as e:
                print(f"  ❌ Error scraping {vtype} violations: {str(e)}")
        
        return violations
    
    def _scrape_building_details(self, driver):
        """Scrape building details from the page"""
        print("🏢 Scraping building details...")
        
        stories_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='STOREYS']]//div[contains(@class,'card-content-botttom')]"
        )
        stories = self.get_element_text(stories_element)

        a_units_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='A UNITS']]//div[contains(@class,'card-content-botttom')]"
        )
        a_units = self.get_element_text(a_units_element)

        b_units_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='B UNITS']]//div[contains(@class,'card-content-botttom')]"
        )
        b_units = self.get_element_text(b_units_element)

        litigation_element = driver.find_element(
            By.CSS_SELECTOR, "span.fs-base > span.fw-bold"
        )
        litigation_number = self.get_element_text(litigation_element)

        aep_element = driver.find_element(
            By.XPATH,
            "//span[text()='Alternate Enforcement Program (AEP)']/../../../../div[contains(@class,'content-right')]//span"
        )
        aep_status = self.get_element_text(aep_element)

        conh_element = driver.find_element(
            By.XPATH,
            "//span[text()='Certification of No Harassment Pilot Program']/../../../../div[contains(@class,'content-right')]//span"
        )
        conh_status = self.get_element_text(conh_element)
        
        return {
            "stories": stories,
            "a_units": a_units,
            "b_units": b_units,
            "litigation": litigation_number,
            "aep_status": aep_status,
            "conh_status": conh_status
        }
    
    def scrape_building_data(self, url):
        """Main method to scrape building data from the given URL"""
        driver, wait = self._setup_driver()
        
        try:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.p-card-content")))
            time.sleep(2)
            
            # Scrape violations
            violations = self._scrape_violations(driver)
            
            # Scrape building details
            building_details = self._scrape_building_details(driver)
            
            # Combine all data into a dictionary
            data = {
                "Stories": building_details["stories"],
                "A Units": building_details["a_units"],
                "B Units": building_details["b_units"],
                "Litigation": building_details["litigation"],
                "AEP Status": building_details["aep_status"],
                "CONH Status": building_details["conh_status"],
                "A Violations": violations["A"],
                "B Violations": violations["B"],
                "C Violations": violations["C"],
                "I Violations": violations["I"],
            }
            
            return data

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Full error traceback:\n{error_details}")
            raise Exception(f"Error scraping data: {str(e)}\nFull traceback: {error_details}")
        finally:
            driver.quit()
