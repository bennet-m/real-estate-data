from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import os
import uuid
from scrapers.hpd_scraper import HPDScraper

app = Flask(__name__)

# Initialize the HPD scraper
hpd_scraper = HPDScraper()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_data():
    """API endpoint to scrape building data"""
    try:
        data = request.get_json()
        borough = data.get('borough')
        block = data.get('block')
        lot = data.get('lot')
        
        if not borough or not block or not lot:
            return jsonify({'error': 'Borough, block, and lot are required'}), 400
        
        # Validate inputs
        try:
            block = int(block)
            lot = int(lot)
        except ValueError:
            return jsonify({'error': 'Block and lot must be valid numbers'}), 400
        
        # Validate borough
        valid_boroughs = ['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island']
        if borough not in valid_boroughs:
            return jsonify({'error': f'Invalid borough. Must be one of: {", ".join(valid_boroughs)}'}), 400
        
        # Scrape the data
        building_data = hpd_scraper.scrape_building_data(borough, block, lot)
        
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
    app.run(debug=True, host='0.0.0.0', port=4000)
