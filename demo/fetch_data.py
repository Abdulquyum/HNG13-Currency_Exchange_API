#!/usr/bin/env python3

import requests
import random
from db import DB
from country import Country
from datetime import datetime

class FetchData:
    def __init__(self):
        self._db = DB()

    def fetch_and_store_countries(self):
        """Fetch countries from REST Countries API and store in database"""
        country_api_url = "https://restcountries.com/v3.1/all?fields=name,capital,region,population,flags,currencies"
        exchange_rate_api_url = "https://open.er-api.com/v6/latest/USD"

        try:
            # Fetch countries data
            print("Fetching countries data...")
            countries_response = requests.get(country_api_url, timeout=30)
            countries_response.raise_for_status()
            countries_data = countries_response.json()
            print(f"Fetched {len(countries_data)} countries")

            # Fetch exchange rates
            print("Fetching exchange rates...")
            exchange_response = requests.get(exchange_rate_api_url, timeout=30)
            exchange_response.raise_for_status()
            exchange_rate_data = exchange_response.json()
            exchange_rates = exchange_rate_data.get('rates', {})
            print("Exchange rates fetched successfully")

            success_count = 0
            for country_info in countries_data:
                try:
                    # Extract country data with better error handling
                    name = country_info.get('name', {}).get('common', 'Unknown')
                    capital = country_info.get('capital', ['N/A'])[0] if country_info.get('capital') else 'N/A'
                    region = country_info.get('region', 'N/A')
                    population = country_info.get('population', 0)
                    
                    # Handle currencies
                    currencies = country_info.get('currencies', {})
                    currency_code = 'N/A'
                    if currencies and isinstance(currencies, dict):
                        currency_code = list(currencies.keys())[0] if currencies else 'N/A'

                    # Skip if required fields are missing
                    if not name or name == 'Unknown' or population is None or not currency_code or currency_code == 'N/A':
                        continue

                    # Get exchange rate (default to 1.0 if not found)
                    exchange_rate = exchange_rates.get(currency_code, 1.0)
                    
                    # Calculate estimated GDP (simplified calculation)
                    gdp_per_capita = random.uniform(1000, 20000)
                    estimated_gdp = population * gdp_per_capita / exchange_rate if exchange_rate and exchange_rate > 0 else population * gdp_per_capita

                    flag_url = country_info.get('flags', {}).get('png', '')
                    last_refreshed_at = datetime.utcnow()

                    self._db.add_country(
                        name=name,
                        capital=capital,
                        region=region,
                        population=population,
                        currency_code=currency_code,
                        exchange_rate=exchange_rate,
                        estimated_gdp=estimated_gdp,
                        flag_url=flag_url,
                        last_refreshed_at=last_refreshed_at
                    )
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error processing country {name}: {e}")
                    continue

            print(f"Successfully stored {success_count} countries")
            return success_count

        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")
            raise
        except Exception as e:
            print(f"Error in fetch_and_store_countries: {e}")
            raise

    def get_all_countries(self):
        """Get all countries from database"""
        return self._db.get_all_countries()

    def get_country_by_name(self, name):
        """Get country by name"""
        return self._db.get_country_by_name(name)

    def delete_country_by_name(self, name):
        """Delete country by name"""
        return self._db.delete_country_by_name(name)