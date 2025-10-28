#!/usr/bin/env python3

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    capital = Column(String(100))
    region = Column(String(100))
    population = Column(Integer)
    currency_code = Column(String(10), nullable=False)
    exchange_rate = Column(Float)
    estimated_gdp = Column(Float)
    flag_url = Column(Text)
    last_refreshed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Country(name='{self.name}', capital='{self.capital}', region='{self.region}')>"