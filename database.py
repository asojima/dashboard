from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///data.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    product = Column(String)
    category = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    date = Column(DateTime, default=datetime.now)