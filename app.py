from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import os
import uuid
from scrapers.hpd_scraper import HPDScraper
from scrapers.bisweb_scraper import BISWEBScraper
from scrapers.dobnow_scraper import DOBNOWScraper

app = Flask(__name__)

# Initialize the scrapers
hpd_scraper = HPDScraper()
bisweb_scraper = BISWEBScraper()
dobnow_scraper = DOBNOWScraper()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_data():
    """API endpoint to scrape building data"""
    try:
        data = request.get_json()
        hpd_url = data.get('hpd_url')
        bisweb_url = data.get('bisweb_url')
        dobnow_url = data.get('dobnow_url')
        
        if not hpd_url and not bisweb_url and not dobnow_url:
            return jsonify({'error': 'At least one URL is required'}), 400
        
        all_data = {}
        
        # Scrape HPD data if URL provided
        if hpd_url:
            # Validate URL format
            if not hpd_url.startswith('http://') and not hpd_url.startswith('https://'):
                hpd_url = 'https://' + hpd_url
            
            print(f"🔍 Scraping HPD data from: {hpd_url}")
            hpd_data = hpd_scraper.scrape_building_data(hpd_url)
            # Prefix HPD data keys to distinguish them
            for key, value in hpd_data.items():
                all_data[f"HPD_{key}"] = value
        
        # Scrape BISWEB data if URL provided
        if bisweb_url:
            # Validate URL format
            if not bisweb_url.startswith('http://') and not bisweb_url.startswith('https://'):
                bisweb_url = 'https://' + bisweb_url
            
            print(f"🔍 Scraping BISWEB data from: {bisweb_url}")
            bisweb_data = bisweb_scraper.scrape_building_data(bisweb_url)
            # Prefix BISWEB data keys to distinguish them
            for key, value in bisweb_data.items():
                all_data[f"BISWEB_{key}"] = value
        
        # Scrape DOBNOW data if URL provided
        if dobnow_url:
            # Validate URL format
            if not dobnow_url.startswith('http://') and not dobnow_url.startswith('https://'):
                dobnow_url = 'https://' + dobnow_url
            
            print(f"🔍 Scraping DOBNOW data from: {dobnow_url}")
            dobnow_data = dobnow_scraper.scrape_building_data(dobnow_url)
            # Prefix DOBNOW data keys to distinguish them
            for key, value in dobnow_data.items():
                all_data[f"DOBNOW_{key}"] = value
        
        # Generate unique filename
        filename = f"building_data_{uuid.uuid4().hex[:8]}.csv"
        filepath = os.path.join('downloads', filename)
        
        # Ensure downloads directory exists
        os.makedirs('downloads', exist_ok=True)
        
        # Create CSV file
        df = pd.DataFrame([all_data])
        df.to_csv(filepath, index=False)
        
        return jsonify({
            'success': True,
            'data': all_data,
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
    app.run(debug=True, host='0.0.0.0', port=4000)
