#!/usr/bin/env python3

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    capital = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String(10), nullable=False)
    exchange_rate = Column(Float, nullable=False)
    estimated_gdp = Column(Float, nullable=False)
    flag_url = Column(String(255), nullable=True)
    last_refreshed_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Country(name='{self.name}', capital='{self.capital}', region='{self.region}')>"
