import random
import unittest
from api.avito import AvitoCatalogAPI
from db.db import AvitoMongoDB
from copy import deepcopy


class AvitoMongoDBTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = AvitoMongoDB(testing=True)
        data = []
        for i in range(100):
            data.append(
                {
                    'location_id': i,
                    'search_query': f'PS{i}',
                    'location_query': 'Москва',
                    'data': [
                        {
                            'timestamp': i * 1000,
                            'counter': i * 10,
                        }
                    ]
                }
            )
        cls.data = data

    def setUp(self):
        self.data_copy = deepcopy(self.data)
        self.db.client.catalog.catalog_data_test.drop()
        col = self.db.client.catalog['catalog_data_test']

    def test_insert_catalog_data(self):
        for doc in self.data_copy:
            catalog_id = self.db.insert_catalog_data(doc['location_id'], doc['location_query'], doc['search_query'],
                                                     doc['data'][0]['counter'], doc['data'][0]['timestamp'])

        saved_data = list(self.db.client.catalog.catalog_data_test.find({}))

        for row in saved_data:
            del row['_id']

        self.assertEqual(self.data, saved_data)

    def test_insert_catalog_data_dict(self):
        for doc in self.data_copy:
            catalog_id = self.db.insert_catalog_data_dict(doc)

        saved_data = list(self.db.client.catalog.catalog_data_test.find({}))

        for row in saved_data:
            del row['_id']

        self.assertEqual(self.data, saved_data)

    def test_get_all_data(self):
        catalog_id_list = self.db.client.catalog.catalog_data_test.insert_many(self.data_copy)
        saved_data = list(self.db.client.catalog.catalog_data_test.find({}))
        for row in saved_data:
            del row['_id']
        self.assertEqual(self.data, saved_data)

    def test_update_catalog_data(self):
        data_example = self.data_copy[random.choice(range(len(self.data_copy)))]
        index = self.db.insert_catalog_data_dict(data_example)
        data_example['data'].append(
            {
                'timestamp': 11111,
                'counter': 22222,
            }
        )
        self.assertTrue(self.db.update_catalog_data(index, data_example['data'][-1]['counter'],
                                                    data_example['data'][-1]['timestamp']))

        del data_example['_id']

        result = self.db.find_catalog_by_id(index)

        self.assertEqual(data_example, result)

    def test_find_catalog_by_id(self):
        for doc in self.data_copy:
            catalog_id = self.db.insert_catalog_data_dict(doc)
        saved_data = self.db.get_all_data()
        key_id = random.choice(range(len(saved_data)))
        reference = self.data[key_id].copy()
        result = self.db.find_catalog_by_id(str(saved_data[key_id]['_id']))
        self.assertEqual(
            reference,
            result
        )

    def test_check_existence(self):
        data = self.data_copy[0]
        result = self.db.check_existence('123', '123')
        self.assertTrue(not result)
        self.db.insert_catalog_data_dict(data)
        result = self.db.check_existence(data['search_query'], data['location_id'])
        self.assertTrue(result)


class AvitoCatalogAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = AvitoCatalogAPI(AvitoMongoDB(testing=True))
        cls.data = [
            ('PS4', 'Москва', '637640'), ('Xbox One', 'Московская область', '637680'),
            ('Мультиварка', 'Пермь', '643700'),
        ]

    def setUp(self):
        self.data_copy = deepcopy(self.data)

    def test_get_location_id(self):
        reference = [x[2] for x in self.data_copy]
        result = []
        locations = [x[1] for x in self.data_copy]
        for location in locations:
            result.append(
                self.catalog._get_location_id(location)
            )
        self.assertEqual(reference, result)

    def test_get_catalog_count(self):
        result = []
        for data in self.data_copy:
            result.append(
                self.catalog._get_catalog_count(data[0], data[2])
            )
        for value in result:
            self.assertTrue(type(value) is int)


if __name__ == '__main__':
    unittest.main()
