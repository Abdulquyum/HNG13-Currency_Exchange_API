#!/usr/bin/env python3

import requests
from sqlalchemy import create_engine
from country import Base
from sqlalchemy.orm import sessionmaker


class DB:
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:root@localhost/countries_db')
        Base.metadata.create_all(self.engine)
        self.__session = None

    @property
    def _session(self):
        if self.__session is None:
            DBSession = sessionmaker(bind=self.engine)
            self.__session = DBSession()
        return self.__session

    def add_country(self, name, capital, region, population, currency_code, exchange_rate, estimated_gdp, flag_url, last_refreshed_at):
        new_country = country(
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
        return self._session.query(country).all()

    def get_country_by_name(self, name):
        return self._session.query(country).filter_by(name=name).first()

    def delete_country_by_name(self, name):
        country_to_delete = self.get_country_by_name(name)
        if country_to_delete:
            self._session.delete(country_to_delete)
            self._session.commit()

            return None
