import sys
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Table, Column, Integer, String, MetaData, Sequence


engine = create_engine('mysql+pymysql://root@localhost/amazon')
# Creating the database if it doesn't exist
if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, Sequence('id'), primary_key=True)
    asin = Column(String(16))
    product_title = Column(String(200))
    product_summary = Column(String(2500))
    technical_details = Column(String(2500))
    product_specifications = Column(String(3500))
    brand = Column(String(50))
    item_weight = Column(String(40))
    product_dimensions = Column(String(40))
    shipping_weight = Column(String(40))
    customer_reviews = Column(String(50))
    customer_ratings = Column(String(50))
    pictures = Column(String(2000))
    price = Column(String(20))
    availability = Column(String(80))

    def __repr__(self):
        return f"<Products(asin={self.asin}, Product Title={self.product_title}, Product Summary={self.product_summary}," \
               f"Technical Details={self.technical_details}, Product Specifications={self.product_specifications} Brand={self.brand}," \
               f"Item Weight={self.item_weight}, Product Dimensions={self.product_dimensions}, Shipping Weight={self.shipping_weight}," \
               f"Customer Reviews={self.customer_reviews}, Customer Ratings={self.customer_ratings}, Pictures={self.pictures}," \
               f"Price={self.price}, Availability={self.availability})>"


# Creating a table 
Products.__table__
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

sys.setrecursionlimit(1000000)

if __name__ == '__main__':
    from amazon_scraper import save_products_info
    from asins_scraper import save_asins

    save_asins()  #  Scrapes asins and saves them to .csv
    save_products_info()  # SQL Scrapes products info from extracted asins and saves them in SQL db
    session.close()


