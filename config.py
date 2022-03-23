class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = ''
    GOOGLEMAPS_KEY = ''

class ProductionConfig(Config):

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'gsale'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'gsale'
    MYSQL_CURSORCLASS = 'DictCursor'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
