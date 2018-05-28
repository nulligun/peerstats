from sqlalchemy import Column, Integer, String, DateTime, func, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Peer(Base):
    __tablename__ = "peers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_added = Column(DateTime, nullable=False, default=func.now())
    date_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    name = Column(String(140), nullable=False)
    enode = Column(String(140), nullable=False)
    address = Column(String(140), nullable=False)
    peer_data = Column(Text, nullable=False)
