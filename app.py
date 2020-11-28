import asyncio
import re

from fastapi import FastAPI
import uvicorn
from api.avito import AvitoCatalogAPI, AvitoCatalog
from db.db import AvitoMongoDB

from settings import HOST, PORT, TIME_PERIOD_MINUTES

app = FastAPI()

db = AvitoMongoDB()

catalog_api = AvitoCatalogAPI(db)


@app.get("/add")
async def add_catalog(query: str, region: str):
    catalog_id = catalog_api.add_catalog(query, region)
    return {
        'code': 200,
        'msg': {
            'catalog_id': catalog_id
        }
    }


@app.get("/stat", response_model=AvitoCatalog)
async def get_catalog(catalog_id: str):
    if not re.match(r'[a-z0-9]{24}', catalog_id):
        return {'code': 400, 'msg': 'Invalid ID'}
    catalog = catalog_api.get_catalog(catalog_id)
    return catalog


async def schedule_update_catalogs():
    while True:
        await asyncio.sleep(TIME_PERIOD_MINUTES)
        catalog_api.update_catalogs()


async def main(scope, receive, send):
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_update_catalogs())
    await app(scope, receive, send)


if __name__ == '__main__':
    uvicorn.run('app:main', host=HOST, port=PORT, loop='asyncio')

