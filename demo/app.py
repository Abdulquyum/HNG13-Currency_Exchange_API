#!/usr/bin/env python3

from flask import Flask, jsonify, request, send_file
import requests
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io
from datetime import datetime
from fetch_data import FetchData

app = Flask(__name__)

# Initialize fetcher
try:
    fetcher = FetchData()
    print("Database initialized successfully")
except Exception as e:
    print(f"Error initializing database: {e}")
    fetcher = None

def validate_country_data(data):
    """Validate country data for required fields"""
    errors = {}
    
    if not data.get('name'):
        errors['name'] = 'is required'
    
    if data.get('population') is None:
        errors['population'] = 'is required'
    elif not isinstance(data.get('population'), (int, float)) or data.get('population') < 0:
        errors['population'] = 'must be a non-negative number'
    
    if not data.get('currency_code'):
        errors['currency_code'] = 'is required'
    
    return errors

@app.before_request
def check_db_connection():
    """Check if database is connected before processing requests"""
    if fetcher is None:
        return jsonify({"error": "Database not connected"}), 500

@app.route('/countries/refresh', methods=['POST'], strict_slashes=False)
def fetch_and_cache_countries():
    """Fetch all countries and exchange rates, then cache them in the database"""
    try:
        result = fetcher.fetch_and_store_countries()
        return jsonify({
            "message": "Countries data fetched and stored successfully.",
            "countries_added": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries', methods=['GET'], strict_slashes=False)
def get_countries():
    """Get all countries from the DB (support filters and sorting)"""
    region = request.args.get('region')
    currency = request.args.get('currency')
    sort = request.args.get('sort')
    
    try:
        countries = fetcher.get_all_countries()
        if not countries:
            return jsonify([]), 200
            
        countries_list = [
            {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
                "currency_code": country.currency_code,
                "exchange_rate": float(country.exchange_rate) if country.exchange_rate else None,
                "estimated_gdp": float(country.estimated_gdp) if country.estimated_gdp else None,
                "flag_url": country.flag_url,
                "last_refreshed_at": country.last_refreshed_at.isoformat() if country.last_refreshed_at else None
            }
            for country in countries
        ]

        # Apply filters
        if region:
            countries_list = [country for country in countries_list if country['region'] == region]
        if currency:
            countries_list = [country for country in countries_list if country['currency_code'] == currency]
        
        # Apply sorting
        if sort == 'gdp_desc':
            countries_list = sorted(countries_list, key=lambda x: x['estimated_gdp'] or 0, reverse=True)
        elif sort == 'gdp_asc':
            countries_list = sorted(countries_list, key=lambda x: x['estimated_gdp'] or 0, reverse=False)
        elif sort == 'population_desc':
            countries_list = sorted(countries_list, key=lambda x: x['population'] or 0, reverse=True)
        elif sort == 'population_asc':
            countries_list = sorted(countries_list, key=lambda x: x['population'] or 0, reverse=False)

        return jsonify(countries_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries/<string:name>', methods=['GET'], strict_slashes=False)
def get_country_by_name(name):
    """Get one country by name"""
    try:
        country = fetcher.get_country_by_name(name)
        if country:
            country_data = {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
                "currency_code": country.currency_code,
                "exchange_rate": float(country.exchange_rate) if country.exchange_rate else None,
                "estimated_gdp": float(country.estimated_gdp) if country.estimated_gdp else None,
                "flag_url": country.flag_url,
                "last_refreshed_at": country.last_refreshed_at.isoformat() if country.last_refreshed_at else None
            }
            return jsonify(country_data), 200
        else:
            return jsonify({"message": "Country not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries/<string:name>', methods=['DELETE'], strict_slashes=False)
def delete_country_by_name(name):
    """Delete a country record"""
    try:
        country = fetcher.get_country_by_name(name)
        if country:
            fetcher.delete_country_by_name(name)
            return jsonify({"message": "Country deleted successfully."}), 200
        else:
            return jsonify({"message": "Country not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'], strict_slashes=False)
def total_countries_and_last_refreshed():
    """Show total countries and last refresh timestamp"""
    try:
        countries = fetcher.get_all_countries()
        total_countries = len(countries)
        
        # Get the most recent refresh timestamp
        last_refreshed_at = None
        if countries:
            valid_timestamps = [country.last_refreshed_at for country in countries if country.last_refreshed_at]
            if valid_timestamps:
                last_refreshed_at = max(valid_timestamps)

        return jsonify({
            "total_countries": total_countries,
            "last_refreshed_at": last_refreshed_at.isoformat() if last_refreshed_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries/image', methods=['GET'], strict_slashes=False)
def get_country_flags():
    """Serve summary image of country flags"""
    try:
        countries = fetcher.get_all_countries()
        
        if not countries:
            return jsonify({"message": "No countries found"}), 404
        
        # Create a summary image
        plt.figure(figsize=(12, 8))
        
        # Prepare data for visualization
        regions = {}
        for country in countries:
            region = country.region or 'Unknown'
            regions[region] = regions.get(region, 0) + 1
        
        # Create visualization
        if len(regions) > 1:
            # Create a pie chart of countries by region
            plt.subplot(1, 2, 1)
            plt.pie(regions.values(), labels=regions.keys(), autopct='%1.1f%%')
            plt.title('Countries by Region')
            
            # Create a bar chart of top 10 countries by population
            plt.subplot(1, 2, 2)
            sorted_countries = sorted(countries, key=lambda x: x.population or 0, reverse=True)[:10]
            country_names = [country.name[:15] + '...' if len(country.name) > 15 else country.name for country in sorted_countries]
            populations = [country.population or 0 for country in sorted_countries]
            plt.barh(country_names, populations)
            plt.title('Top 10 Countries by Population')
            plt.xlabel('Population')
        else:
            # If we don't have enough regions, just show one chart
            plt.barh(list(regions.keys()), list(regions.values()))
            plt.title('Countries by Region')
            plt.xlabel('Number of Countries')
        
        plt.tight_layout()
        
        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png', as_attachment=False, download_name='countries_summary.png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, host="0.0.0.0", debug=True)