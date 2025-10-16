# Real Estate Data Scraper

A web application that scrapes building data from NYC HPD Online and provides it as a downloadable CSV file.

## Features

- **Modern Web UI**: Beautiful, responsive interface built with Bootstrap
- **URL Input**: Submit any HPD Online building overview URL
- **Data Scraping**: Extracts comprehensive building information including:
  - Stories count
  - A Units and B Units
  - Litigation number
  - AEP Status
  - CONH Status
  - Violation counts (A, B, C, I classes)
- **CSV Download**: Download scraped data as a CSV file
- **Real-time Feedback**: Loading states and error handling

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome browser installed (required for Selenium)

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter a valid HPD Online building overview URL in the input field
2. Click "Scrape Building Data"
3. Wait for the scraping to complete
4. View the extracted data in the table
5. Click "Download CSV" to save the data

## Example URL

```
https://hpdonline.nyc.gov/hpdonline/building/314419/overview
```

## API Endpoints

- `GET /` - Serves the main web interface
- `POST /scrape` - Scrapes building data from provided URL
- `GET /download/<filename>` - Downloads CSV file

## Technical Details

- **Backend**: Flask web framework
- **Web Scraping**: Selenium WebDriver with Chrome
- **Data Processing**: Pandas for CSV generation
- **Frontend**: HTML, CSS, JavaScript with Bootstrap styling
- **Headless Mode**: Chrome runs in headless mode for server deployment

## File Structure

```
real-estate-data/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── downloads/            # Generated CSV files (created automatically)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Notes

- The application runs Chrome in headless mode for better performance
- CSV files are automatically cleaned up (you may want to implement cleanup logic)
- The scraper is specifically designed for NYC HPD Online building overview pages
