#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from country import Base, Country

class DB:
    def __init__(self):
        # Use SQLite database file
        self.engine = create_engine('sqlite:///countries_db.db')
        Base.metadata.create_all(self.engine)
        self.__session = None

    @property
    def _session(self):
        if self.__session is None:
            DBSession = sessionmaker(bind=self.engine)
            self.__session = DBSession()
        return self.__session

    def add_country(self, name, capital, region, population, currency_code, exchange_rate, estimated_gdp, flag_url, last_refreshed_at):
        # Check if country already exists
        existing_country = self._session.query(Country).filter_by(name=name).first()
        if existing_country:
            # Update existing country
            existing_country.capital = capital
            existing_country.region = region
            existing_country.population = population
            existing_country.currency_code = currency_code
            existing_country.exchange_rate = exchange_rate
            existing_country.estimated_gdp = estimated_gdp
            existing_country.flag_url = flag_url
            existing_country.last_refreshed_at = last_refreshed_at
            self._session.commit()
            return existing_country
        else:
            # Create new country
            new_country = Country(
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
            self._session.add(new_country)
            self._session.commit()
            return new_country

    def get_all_countries(self):
        return self._session.query(Country).all()

    def get_country_by_name(self, name):
        return self._session.query(Country).filter_by(name=name).first()

    def delete_country_by_name(self, name):
        country_to_delete = self.get_country_by_name(name)
        if country_to_delete:
            self._session.delete(country_to_delete)
            self._session.commit()
        return None

    def clear_countries(self):
        """Clear all countries from the database"""
        try:
            self._session.query(Country).delete()
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e