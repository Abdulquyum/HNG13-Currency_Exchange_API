#!/usr/bin/env python3

from flask import Flask, jsonify, request
import requests
from fetch_data import FetchData

app = Flask(__name__)

fetcher = FetchData()


country_api_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
exchange_rate_api_url = "https://open.er-api.com/v6/latest/USD"


@app.route('/countries/refresh', methods=['POST'], strict_slashes=False)
def fetch_and_cache_countries():
    try:
        fetcher.fetch_and_store_countries()
        return jsonify({"message": "Countries data fetched and stored successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/countries', methods=['GET'], strict_slashes=False)
# def get_countries():
#     try:
#         countries_data = requests.get(country_api_url).json()
#         return jsonify(countries_data), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/countries', methods=['GET'], strict_slashes=False)
def get_countries():
    region = request.args.get('region')
    currency = request.args.get('currency')
    sort = request.args.get('estimated_gdp', desc=True)
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
        if sort:
            countries_list = sorted(countries_list, key=lambda x: x['estimated_gdp'], reverse=True)

        return jsonify(countries_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/countries/<string:name>', methods=['GET'], strrict_slashes=False)
def get_country_by_name(name):
    try:
        country = fetcher.get_country_by_name(name)
        if country:
            country_data = {
                "name": country.name,
                "capital": country.capital,
                "region": country.region,
                "population": country.population,
                "currency_code": country.currency_code,
                "exchnage_rate": country.exchange_rate,
                "estimated_gdp": country.estimated_gdp,
                "flag_url": country.flag_url,
                "last_refreshed_at": country.last_refreshed_at.isoformat()
            }

            return jsonify(country_data), 200
        else:
            return jsonify({"message": "Country not found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

# @app.route('/exchangeRate', methods=['GET'], strict_slashes=False)
# def get_exchange_rate():
#     try:
#         exchange_rate_data = requests.get(exchange_rate_api_url).json()
#         return jsonify(exchange_rate_data), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, host="0.0.0.0", debug=True)
