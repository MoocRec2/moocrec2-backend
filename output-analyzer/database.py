"""
Responsible for handling MongoDB database connection.
"""

from pymongo import MongoClient

MONGO_CONFIG = {
    'host': '3.228.104.174',
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

    :param config
        A dict that contains following info.
        - host
        - authDb
        - user
        - password
        - port
    """
    global CLIENT

    if CLIENT is None:
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
    global CLIENT

    if CLIENT is not None:
        CLIENT.close()
        CLIENT = None


def database(database_name):
    """
    Returns a database object.

    :param database_name
        Name of the database in MongoDB.

    :returns mongodb database object.
    """
    global CLIENT

    init_mongo(MONGO_CONFIG)
    db = CLIENT[database_name]

    return db

def collection(database_name, collection_name):
    """
    If a collection is preferred instead of retrieving,
    the database first.

    :param database_name
        Name of the database in MongoDB.
    :param collection_name
        Name of the collection in database.

    :returns mongodb collection object.
    """
    db = database(database_name)
    collection = db[collection_name]

    return collection


def document_exists(database_name, collection_name, identifier_key, identifier_value):
    """
    Checks if a document/entry exists in the given collection.

    :param database_name
        Name of the database in MongoDB.
    :param collection_name
        Name of the collection in database.
    :param identifier_key
        Attribute that is used to uniquely identify each entry/document.
    :param identifier_value
        Value of the identifier(akin primary key value) which we are querying for.

    :returns bool -> True if entry exists.
    """

    collection_ = collection(database_name, collection_name)
    return collection_.count_documents({identifier_key: identifier_value}) > 0

def get_one(database_name, collection_name, identifier_key, identifier_value):
    """
    Returns a single entry/document.

    :param database_name
        Name of the database in MongoDB.
    :param collection_name
        Name of the collection in database.
    :param identifier_key
        Attribute that is used to uniquely identify each entry/document.
    :param identifier_value
        Value of the identifier(akin primary key value) which we are querying for.

    :returns mongodb document object.
    """

    collection_ = collection(database_name, collection_name)
    result = collection_.find_one({identifier_key: identifier_value})

    return result

def save(database_name, collection_name, identifier_key, identifier_value, values):
    """
    Creates a document or updates existing one.

    :param database_name
        Name of the database in MongoDB.
    :param collection_name
        Name of the collection in database.
    :param identifier_key
        Attribute that is used to uniquely identify each entry/document.
    :param identifier_value
        Value of the identifier(akin primary key value) which we are querying for.
    :param values
        A dictionary that contains new values.
    """

    exists = document_exists(database_name, collection_name, identifier_key, identifier_value)

    if exists:
        collection_ = collection(database_name, collection_name)
        collection_.update_one({identifier_key: identifier_value}, {'$set': values})
    else:
        collection_ = collection(database_name, collection_name)
        values[identifier_key] = identifier_value   # prep unique identifier.
        collection_.insert_one(values)

    
def main():
    global CLIENT, MONGO_CONFIG
    print(CLIENT)
    
    v = document_exists('moocrec-v2', 'courses', 'key', 'course-v1:UWashingtonX+PM-IT-002x+2T2019')
    r = get_one('moocrec-v2', 'courses', 'key', 'course-v1:UWashingtonX+PM-IT-002x+2T2019__')
    s = save('moocrec-v2', 'users', 'username', 'aliyanage44', {'test_value_2': 5})
    print(r)
    print(CLIENT)
    deinit_mongo()
    print(CLIENT)

#main()