from sqlalchemy import Column, Integer, String, Float

from database import Base

"""
This class represents the table in the DB. all the lines below are the columns in that table.
"""


class Addresses(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    loc_lat = Column(Float)
    loc_lon = Column(Float)
