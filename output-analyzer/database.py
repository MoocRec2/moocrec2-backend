"""
Responsible for handling MongoDB database connection.
"""

from pymongo import MongoClient

MONGO_CONFIG = {
    'host': '52.66.18.67',
    'authDb': 'moocrec-v2',
    'user': 'user',
    'password': 'password',
    'port': '27017'
}

CLIENT = None

def init_mongo(config):
    """
    Initiates a connection to MongoDB.
    NOTE: Keep it singleton ;)
    """

    if CLIENT is not None:
        connection_url = 'mongodb://{username}:{password}@{host}:{port}/?authSource={authDb}'.format(
            username=MONGO_CONFIG['user'],
            password=MONGO_CONFIG['password'],
            host=MONGO_CONFIG['host'],
            port=MONGO_CONFIG['port'],
            authDb=MONGO_CONFIG['authDb']
        )
        CLIENT = MongoClient(connection_url)

    return CLIENT


def deinit_mongo():
    """
    Close the DB connection.
    """
    
    if CLIENT is not None:
        CLIENT.close()
        CLIENT = None

