#!/usr/bin/env python3

from flask import Flask, jsonify, request
import requests
from fetch_data import FetchData

app = Flask(__name__)

fetcher = FetchData()

@app.route('/countries/refresh', methods=['POST'], strict_slashes=False)
def fetch_and_cache_countries():
    try:
        fetcher.fetch_and_store_countries()
        return jsonify({"message": "Countries data fetched and stored successfully."}), 200

    except requests.RequestException as e:
        return jsonify({ "error": f"External data source unavailable", "details": f"Could not fetch data from {e.request.url}"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries', methods=['GET'], strict_slashes=False)
def get_countries():
    region = request.args.get('region')
    currency = request.args.get('currency')
    sort = request.args.get('sort')
    try:
        countries = fetcher.get_all_countries()
        countries_list = [
            {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
                "currency_code": country.currency_code,
                "exchange_rate": country.exchange_rate,
                "estimated_gdp": country.estimated_gdp,
                "flag_url": country.flag_url,
                "last_refreshed_at": country.last_refreshed_at.isoformat()
            }
            for country in countries
        ]

        if region:
            countries_list = [country for country in countries_list if country['region'] == region]
        if currency:
            countries_list = [country for country in countries_list if country['currency_code'] == currency]

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
        return jsonify({"error": "Internal server error"}), 500

@app.route('/countries/<string:name>', methods=['GET'], strict_slashes=False)
def get_country_by_name(name):
    try:
        country = fetcher.get_country_by_name(name)
        if country:
            # Validate required fields before returning
            errors = {}
            if not getattr(country, 'name', None):
                errors['name'] = 'is required'

            # population: must exist and be a non-negative integer
            pop = getattr(country, 'population', None)
            if pop is None:
                errors['population'] = 'is required'
            else:
                try:
                    if int(pop) < 0:
                        errors['population'] = 'must be a non-negative integer'
                except Exception:
                    errors['population'] = 'must be an integer'

            if not getattr(country, 'currency_code', None):
                errors['currency_code'] = 'is required'

            if errors:
                return jsonify({"error": "Validation failed", "details": errors}), 400

            country_data = {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
                "currency_code": country.currency_code,
                "exchange_rate": country.exchange_rate,
                "estimated_gdp": country.estimated_gdp,
                "flag_url": country.flag_url,
                "last_refreshed_at": country.last_refreshed_at.isoformat() if country.last_refreshed_at else None
            }

            return jsonify(country_data), 200
        else:
            return jsonify({"message": "Country not found."}), 404

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/countries/<string:name>', methods=['DELETE'], strict_slashes=False)
def delete_country_by_name(name):
    try:
        country = fetcher.get_country_by_name(name)
        if country:
            fetcher.delete_country_by_name(name)
            return jsonify({"message": "Country deleted successfully."}), 200
        else:
            return jsonify({"message": "Country not found."}), 404

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/status', methods=['GET'], strict_slashes=False)
def total_countries_and_last_refreshed():
    try:
        countries = fetcher.get_all_countries()
        total_countries = len(countries)
        last_refreshed_at = max(country.last_refreshed_at for country in countries) if countries else None

        return jsonify({
            "total_countries": total_countries,
            "last_refreshed_at": last_refreshed_at.isoformat() if last_refreshed_at else None
        }), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/countries/image', methods=['GET'], strict_slashes=False)
def get_country_flags():
    '''
    Image Generation
    When /countries/refresh runs:
    After saving countries in the database, generate an image (e.g., cache/summary.png) containing:
    Total number of countries
    Top 5 countries by estimated GDP
    Timestamp of last refresh
    Save the generated image on disk at cache/summary.png.
    Add a new endpoint:
    GET /countries/image → Serve the generated summary image
    If no image exists, return:
    { "error": "Summary image not found" }
    '''

    try:
        with open('cache/summary.png', 'rb') as image_file:
            image_data = image_file.read()
        return (image_data, 200, {
            'Content-Type': 'image/png',
            'Content-Disposition': 'inline; filename="summary.png"'
        })
    except FileNotFoundError:
        return jsonify({"error": "Summary image not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(port=3000, host="0.0.0.0", debug=True)
