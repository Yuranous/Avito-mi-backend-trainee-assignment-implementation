import abc
import datetime

from bson import ObjectId
from pymongo import MongoClient

from settings import MONGO_HOST, MONGO_PORT, \
    MONGO_DB_NAME, MONGO_DB_COL_PROD_NAME, MONGO_DB_COL_TEST_NAME, \
    MONGO_USERNAME, MONGO_PASSWORD


class AvitoDB(abc.ABC):
    @abc.abstractmethod
    def insert_catalog_data_dict(self, document: dict) -> str:
        pass

    @abc.abstractmethod
    def insert_catalog_data(self, location_id, location_query, search_query, counter,
                            timestamp=datetime.datetime.now().timestamp()) -> str:
        pass

    @abc.abstractmethod
    def update_catalog_data(self, catalog_id, counter, timestamp=datetime.datetime.now().timestamp()):
        pass

    @abc.abstractmethod
    def find_catalog_by_id(self, catalog_id):
        pass

    @abc.abstractmethod
    def get_all_data(self):
        pass

    @abc.abstractmethod
    def check_existence(self, search_query, location_id):
        pass


class AvitoMongoDB(AvitoDB):
    def __init__(self, testing=False):
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD)
        self.client = client
        col_name = MONGO_DB_COL_PROD_NAME if not testing else MONGO_DB_COL_TEST_NAME
        catalog_db = client[MONGO_DB_NAME]
        catalog_col_data = catalog_db[col_name]
        catalog_col_data.drop()
        if testing:
            self.col_client = client.catalog.catalog_data_test
        else:
            self.col_client = client.catalog.catalog_data

    def insert_catalog_data_dict(self, document: dict) -> str:
        return self.col_client.insert_one(document).inserted_id

    def insert_catalog_data(self, location_id, location_query, search_query, counter,
                            timestamp=datetime.datetime.now().timestamp()) -> str:
        return self.col_client.insert_one(
            {
                'location_id': location_id,
                'search_query': search_query,
                'location_query': location_query,
                'data': [
                    {
                        'timestamp': timestamp,
                        'counter': counter,
                    }
                ]
            }
        ).inserted_id

    def update_catalog_data(self, catalog_id, counter, timestamp=datetime.datetime.now().timestamp()):
        result = self.find_catalog_by_id(catalog_id)
        result['data'].append(
            {
                'timestamp': timestamp,
                'counter': counter,
            }
        )
        modified = self.col_client.update_one({'_id': catalog_id}, {'$set': result})
        return modified.modified_count == 1

    def find_catalog_by_id(self, catalog_id):
        result = self.col_client.find_one({'_id': ObjectId(catalog_id)})
        del result['_id']
        return result

    def get_all_data(self):
        return list(self.col_client.find({}))

    def check_existence(self, search_query, location_id):
        result = self.col_client.find_one(
            {
                'search_query': search_query,
                'location_id': location_id,
            }
        )
        return bool(result)
