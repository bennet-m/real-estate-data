from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import uuid
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def get_element_text(element):
    """Extract text from element using multiple methods for robustness"""
    # Try different text extraction methods in order of preference
    text = element.text or element.get_attribute('textContent') or element.get_attribute('innerText')
    return text.strip() if text else ""

def scrape_building_data(url):
    """Scrape building data from the given URL"""
    # Configure Chrome options with proper window size
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size to ensure content loads
    chrome_options.add_argument("--start-maximized")  # Start maximized
    chrome_options.add_argument("--disable-web-security")  # Disable web security for better compatibility
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # Disable compositor for stability
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    # Ensure window is properly sized for content loading
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.p-card-content")))
        time.sleep(2)

        # Scrape data
        print("🔍 Scraping violation data...")
        violations = {}
        violation_types = ["A", "B", "C", "I"]
        
        for vtype in violation_types:
            try:
                element = driver.find_element(By.XPATH, f"//span[contains(normalize-space(.),'{vtype} Class')]/span[@class='fw-bold']")
                text = get_element_text(element)
                print(f"  {vtype} Class violations: '{text}'")
                violations[vtype] = int(text) if text else 0
            except Exception as e:
                print(f"  ❌ Error scraping {vtype} violations: {str(e)}")
                violations[vtype] = 0
        print("🏢 Scraping building details...")
        
        stories_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='STOREYS']]//div[contains(@class,'card-content-botttom')]"
        )
        stories = get_element_text(stories_element)

        a_units_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='A UNITS']]//div[contains(@class,'card-content-botttom')]"
        )
        a_units = get_element_text(a_units_element)

        b_units_element = driver.find_element(
            By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='B UNITS']]//div[contains(@class,'card-content-botttom')]"
        )
        b_units = get_element_text(b_units_element)

        litigation_element = driver.find_element(
            By.CSS_SELECTOR, "span.fs-base > span.fw-bold"
        )
        litigation_number = get_element_text(litigation_element)

        aep_element = driver.find_element(
            By.XPATH,
            "//span[text()='Alternate Enforcement Program (AEP)']/../../../../div[contains(@class,'content-right')]//span"
        )
        aep_status = get_element_text(aep_element)

        conh_element = driver.find_element(
            By.XPATH,
            "//span[text()='Certification of No Harassment Pilot Program']/../../../../div[contains(@class,'content-right')]//span"
        )
        conh_status = get_element_text(conh_element)

        driver.quit()

        # Combine all data into a dictionary for pandas
        data = {
            "Stories": stories,
            "A Units": a_units,
            "B Units": b_units,
            "Litigation": litigation_number,
            "AEP Status": aep_status,
            "CONH Status": conh_status,
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

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_data():
    """API endpoint to scrape building data"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        # Scrape the data
        building_data = scrape_building_data(url)
        
        # Generate unique filename
        filename = f"building_data_{uuid.uuid4().hex[:8]}.csv"
        filepath = os.path.join('downloads', filename)
        
        # Ensure downloads directory exists
        os.makedirs('downloads', exist_ok=True)
        
        # Create CSV file
        df = pd.DataFrame([building_data])
        df.to_csv(filepath, index=False)
        
        return jsonify({
            'success': True,
            'data': building_data,
            'download_url': f'/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve CSV file for download"""
    try:
        filepath = os.path.join('downloads', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
