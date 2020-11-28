import json
from pydantic import BaseModel
import cfscrape
from requests import Response

from db.db import AvitoDB


def send_request(params: dict, url: str) -> Response:
    with cfscrape.create_scraper() as scraper:
        return scraper.get(
            url.format(**params)
        )


class AvitoCatalogAPI:
    REQUEST_CATALOG = 'https://www.avito.ru/js/catalog?locationId={location_id}&name={name}'
    REQUEST_LOCATION = 'https://www.avito.ru/web/1/slocations?limit={limit}&q={q}'

    def __init__(self, db: AvitoDB):
        self.db = db

    def _get_location_id(self, location_query: str) -> str:
        """
        Method to get location identifier from Avito API. It creates dictionary with limit and query arguments and then
        send request with this named function from this module.
        :param location_query: name of the location
        :return: location identifier
        """
        params = {
            'limit': 1,
            'q': location_query,
        }
        response = send_request(params, self.REQUEST_LOCATION)

        try:
            return str(json.loads(response.text)['result']['locations'][0]['id'])
        except KeyError:
            raise KeyError('Превышен лимит запросов от программы')

    def _get_catalog_count(self, search_query: str, location_id: str) -> int:
        """
        Method to get catalog counter for specific search and location pair. It creates dictionary with location_id and
        name (query) arguments and then send request with this named function from this module.
        :param search_query: search (for what we looking for)
        :param location_id: location identifier from Avito API
        :return: counter (number of items in catalog)
        """
        params = {
            'name': search_query,
            'location_id': location_id,
        }

        response = send_request(params, self.REQUEST_CATALOG)

        try:
            return json.loads(response.text)['totalCount']
        except KeyError:
            raise KeyError('Превышен лимит запросов от программы')

    def add_catalog(self, search_query, location_query):
        """
        Method to add new search-location pair to service.
        :param search_query: search (for what we looking for)
        :param location_query: name of the location (region)
        :return:
        """
        location_id = self._get_location_id(location_query)
        catalog_counter = self._get_catalog_count(search_query, location_id)
        catalog_id = self.db.insert_catalog_data(location_id, location_query, search_query, catalog_counter)
        return str(catalog_id)

    def get_catalog(self, catalog_id):
        """
        Method to get existing catalog information by its identifier in service.
        :param catalog_id: catalog identifier in service
        :return: catalog information
        """
        result = self.db.find_catalog_by_id(catalog_id)
        result['catalog_id'] = catalog_id
        return AvitoCatalog(**result)

    def update_catalogs(self):
        """
        Method to update data field in all catalogs (add new information)
        :return: None
        """
        result = []
        catalogs = self.db.get_all_data()
        for catalog in catalogs:
            new_counter = self._get_catalog_count(catalog['search_query'], catalog['location_id'])
            self.db.update_catalog_data(
                catalog['_id'],
                new_counter
            )


class AvitoCatalog(BaseModel):
    catalog_id: str
    search_query: str
    location_query: str
    location_id: str
    data: list
