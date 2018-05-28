from models import *
from configobj import ConfigObj
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import json
import requests


config = ConfigObj(".env")
engine = create_engine("mysql+mysqldb://%(database_user)s:%(database_password)s@%(database_host)s/%(database_name)s" % config, isolation_level="READ UNCOMMITTED", pool_recycle=4)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


result = requests.post(config['rpc_endpoint'], '{"method":"parity_netPeers","params":[],"id":1,"jsonrpc":"2.0"}', headers={'Content-type': 'application/json'})

x = 1

