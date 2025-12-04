from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper


class HPDScraper(BaseScraper):
    """Scraper for HPD Online website to extract building data"""
    
    def _scrape_violations(self, driver):
        """Scrape violation data from the page"""
        print("🔍 Scraping violation data...")
        violations = {}
        violation_types = ["A", "B", "C", "I"]
        
        for vtype in violation_types:
            try:
                element = driver.find_element(By.XPATH, f"//span[contains(normalize-space(.),'{vtype} Class')]/span[@class='fw-bold']")
                text = self.get_element_text(element)
                print(f"  {vtype} Class violations: '{text}'")
                violations[vtype] = int(text) if text else 0
            except Exception as e:
                print(f"  ❌ Error scraping {vtype} violations: {str(e)}")
                violations[vtype] = 0
        
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
    
    def _scrape_data(self, driver, wait):
        """Scrape building data from HPD page"""
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

    def scrape_building_data(self, building_id_or_url):
        """Accept either a HPD building id (digits) or a full URL.

        If a building id is provided, construct the HPD overview URL
        and navigate there. Otherwise, treat the input as a URL and
        use the base class navigation.
        """
        # Normalize input
        input_str = str(building_id_or_url).strip()

        # If the input looks like a building id (all digits), construct the overview URL
        if input_str.isdigit():
            url = f"https://hpdonline.nyc.gov/hpdonline/building/{input_str}/overview"
            print(f"🌐 HPD building id provided — navigating to: {url}")
            return super().scrape_building_data(url)

        # Otherwise assume it's a URL (or hostname) and let the base class handle it
        return super().scrape_building_data(input_str)

