from restartdb import *
from csvloader import populate
import time

try:
    session = Session()
    Base.metadata.create_all(engine)
except:
    print("Could not create database")

time.sleep(5)

try:
    populate()
except:
    print("could not populate the database")
