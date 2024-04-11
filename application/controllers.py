from datetime import datetime

from aiohttp.web import json_response
from ccxt import BadSymbol
from sqlalchemy import select, delete, func

from application import models


async def get_price(request):
    """Fetches and stores the current price of a cryptocurrency."""
    currency = request.match_info['currency']
    if currency == 'history':
        return await get_statistics(request)
    else:
        try:
            exchange = request.app['exchange']

            ticker = exchange.fetch_ticker(f'{currency}/USDT')
            price = ticker['bid']

            timestamp = datetime.utcnow().replace(microsecond=0)

            async with request.app['db'].acquire() as conn:
                query = "INSERT INTO statistics (currency, price, date_) VALUES ($1, $2, $3)"
                await conn.execute(query, currency, price, timestamp)

            return json_response(text=f'Price for {currency} is {price} USDT.')
        except BadSymbol:
            return json_response(text=f"Currency '{currency}' not found.", status=400)
        except Exception:
            return json_response(text="Internal server error", status=500)


async def get_statistics(request):
    """Retrieves price history data from the database with pagination."""
    page_param = request.query.get('page')

    try:
        page = int(page_param)
        if page <= 0:
            raise ValueError("Invalid page number: must be greater than 0")
    except (TypeError, ValueError):
        return json_response(text="Invalid page parameter", status=400)

    async with request.app['db'].acquire() as conn:
        total_count_query = select(func.count()).select_from(models.statistics)
        total_count = await conn.fetchval(total_count_query)

        total_pages = (total_count + 9) // 10

        offset = (page - 1) * 10
        query = select(models.statistics.c.id, models.statistics.c.currency,
                       models.statistics.c.date_, models.statistics.c.price).limit(10).offset(offset)
        result = await conn.fetch(query)

    data = [
        {
            "id": row[0],
            "currency": row[1],
            "date": row[2].isoformat(),
            "price": row[3],
        }
        for row in result
    ]

    return json_response({
        "data": data,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
        }
    })


async def delete_statistics(request):
    """Delete all records in database."""
    async with request.app['db'].acquire() as conn:
        query = delete(models.statistics)
        await conn.execute(query)
    return json_response(text='All records have been deleted.')
