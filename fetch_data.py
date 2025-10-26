#!/usr/bin/env python3

from db import DB
from country import country
from datetime import datetime


class FetchData:
    def __init__(self):
        self._db = DB()

    def fetch_and_store_countries(self):
        country_api_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
        exchange_rate_api_url = " https://open.er-api.com/v6/latest/USD"

        try:
            countries_data = requests.get(country_api_url).json()
            exchange_rate_data = requests.get(exchange_rate_api_url).json()
            exchange_rates = exchange_rate_data.get('rates', {})

            for country_info in countries_data:
                name = country_info.get('name')
                capital = country_info.get('capital')
                region = country_info.get('region')
                population = country_info.get('population')

                currencies = country_info.get('currencies', [])
                currency_code = currencies[0]['code'] if currencies else 'N/A'

                exchange_rate = exchange_rates.get(currency_code)
                estimated_gdp = population * random.randint(1000, 2000) / exchange_rate

                flag_url = country_info.get('flag')
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

        except Exception as e:
            print(f"Error fetching or storing countries data: {e}")
