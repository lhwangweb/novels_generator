from mongoengine import *

# Mongo 連線資訊
MONGO_USER="test_user"
MONGO_PASSWD="test_password"
MONGO_HOST= "mongodb"
MONGO_DBNAME = "novels"

def mongo_connection():
    connect(
        alias='default',
        host = MONGO_HOST,
        username = MONGO_USER,
        password = MONGO_PASSWD,
        db = MONGO_DBNAME,
        port = 27017,    
    )
