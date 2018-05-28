from models import *
from sqlalchemy import create_engine
from configobj import ConfigObj
from sqlalchemy.orm import sessionmaker


config = ConfigObj(".env")
engine = create_engine("mysql+mysqldb://%(database_user)s:%(database_password)s@%(database_host)s/%(database_name)s?charset=utf8" % config, encoding='utf-8', isolation_level="READ UNCOMMITTED")

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("Tables have been recreated")

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
