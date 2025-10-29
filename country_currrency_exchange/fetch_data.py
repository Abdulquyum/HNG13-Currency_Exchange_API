#!/usr/bin/env python3

from db import DB
from country import Country
from datetime import datetime, timezone
import random
import requests
from image_generator import ImageGenerator

class FetchData:
    def __init__(self):
        self._db = DB()
        self.image_generator = ImageGenerator()

    def fetch_and_store_countries(self):
        country_api_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
        exchange_rate_api_url = " https://open.er-api.com/v6/latest/USD"

        try:
            countries_response = requests.get(country_api_url, timeout=20)
            countries_response.raise_for_status()
            countries_data = countries_response.json()

            exchange_rate_response = requests.get(exchange_rate_api_url, timeout=20)
            exchange_rate_response.raise_for_status()
            exchange_rate_data = exchange_rate_response.json()
            exchange_rates = exchange_rate_data.get('rates', {})

            for country_info in countries_data:
                try:
                    name = country_info.get('name')
                    capital = country_info.get('capital', None)
                    region = country_info.get('region', None)
                    population = country_info.get('population', 0)

                    currencies = country_info.get('currencies', [])
                    currency_code = None
                    if currencies and isinstance(currencies, list) and len(currencies) > 0:
                        currency_code = currencies[0].get('code')


                    if not name or population is None or not currency_code:
                        continue

                    exchange_rate = exchange_rates.get(currency_code) if currency_code else None

                    if exchange_rate and exchange_rate != 0:
                        estimated_gdp = population * random.randint(1000, 2000) / exchange_rate
                    else:
                        exchange_rate = 0.0
                        estimated_gdp = 0

                    flag_url = country_info.get('flag')
                    last_refreshed_at = datetime.now(timezone.utc)


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

                except Exception as e:
                    print(f"Failed to insert country {name}: {e}")

            countries = self.get_all_countries()
            self.image_generator.generate_summary_image(countries)

        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")
            raise

        except Exception as e:
            print(f"Error fetching or storing countries data: {e}")

    def get_all_countries(self):
        return self._db.get_all_countries()

    def get_country_by_name(self, name):
        return self._db.get_country_by_name(name)

    def delete_country_by_name(self, name):
        country_to_delete = self.get_country_by_name(name)
        if country_to_delete:
            self._db.delete_country_by_name(name)
            return None
