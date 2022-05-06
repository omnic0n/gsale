class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = '4T3*%go^Gcn7TrYm'
    GOOGLEMAPS_KEY = 'AIzaSyCx0uvY8tyZe7gfOKjEZIgJL__ijm0ojZ0'

class ProductionConfig(Config):

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'gsale'
    MYSQL_PASSWORD = 'DR1wZcjTF7858gnu'  
    MYSQL_DB = 'gsale'
    MYSQL_CURSORCLASS = 'DictCursor'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
