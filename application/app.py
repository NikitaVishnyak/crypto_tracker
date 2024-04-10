import os

import asyncpgsa
from aiohttp import web
from ccxt import kucoin

from application.controllers import get_price, get_statistics, delete_statistics

username = os.environ.get('SQL_USER')
password = os.environ.get('SQL_PASSWORD')
db_name = os.environ.get('SQL_DB')


async def create_app():
    """Create, configure and return the aiohttp application instance."""
    app = web.Application()
    app.add_routes([web.get('/price/{currency}', get_price),
                    web.get('/price/history', get_statistics),
                    web.delete('/price/history', delete_statistics)])
    app['exchange'] = kucoin()
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    """Establish a connection pool to the database."""
    app['db'] = await asyncpgsa.create_pool(dsn=f'postgresql://{username}:{password}@localhost:5432/{db_name}')


async def on_shutdown(app):
    """Close the database connection pool."""
    await app['db'].close()
