import os

# MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'catalog')
MONGO_DB_COL_PROD_NAME = os.getenv('MONGO_DB_COL_PROD_NAME', 'catalog_data')
MONGO_DB_COL_TEST_NAME = os.getenv('MONGO_DB_COL_TEST_NAME', 'catalog_data_test')
MONGO_HOST = os.getenv('MONGO_HOST', '0.0.0.0')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'root')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'example')

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', 8127)

TIME_PERIOD_MINUTES = os.getenv('TIME_PERIOD_MINUTES', 60) * 60
