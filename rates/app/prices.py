import datetime
from decimal import Decimal
from typing import Optional, Sequence, Tuple

from rates.app.models import AveragePrice, AveragePrices, RatesRequest
from sqlalchemy import text
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine


async def get_average_prices(
    engine: AsyncEngine, request: RatesRequest
) -> AveragePrices:
    """
    Finds average prices for given origin, destination and date range

    :param engine: sqlalchemy engine instance
    :type engine: AsyncEngine
    :param request: request with origin, destination and date range
    :type request: RatesRequest
    :return: list of average prices for each day in date range
    :rtype: AveragePrices
    """
    async with engine.connect() as connection:
        prices = await get_prices_for_request(connection, request)

    return process_prices(prices)


async def get_prices_for_request(
    connection: AsyncConnection, request: RatesRequest
) -> Sequence[Row]:
    """
    Fetches day, average prices and prices amount for given ports and dates

    :param connection: sqlalchemy connection instance
    :type connection: AsyncConnection
    :param request: request with origin, destination and date range
    :type request: RatesRequest
    :return: sequence of rows with day, average prices and prices amount
    :rtype: Sequence[Row]
    """
    prices_per_day_query = await connection.execute(
        text(
            """
            WITH prices_per_day as (
                SELECT day, avg(price) AS avg_price, count(price) AS prices_count
                FROM prices
                JOIN (SELECT code FROM codes WHERE key = :origin) origin_codes
                    ON orig_code = origin_codes.code
                JOIN (SELECT code FROM codes WHERE key = :destination) destination_codes
                    ON prices.dest_code = destination_codes.code
                WHERE day BETWEEN :date_from AND :date_to
                GROUP BY day
            ),
            missing_dates AS (
                SELECT day, 0 AS avg_price, 0 AS prices_count
                FROM (
                    SELECT generate_series(:date_from ::date, :date_to, '1 day')::date
                    AS day
                ) date_range
                WHERE day NOT IN (SELECT day FROM prices_per_day)
            )
            SELECT day, avg_price, prices_count FROM prices_per_day
            UNION
            SELECT day, avg_price, prices_count FROM missing_dates
            ORDER BY day
            """
        ),
        {
            "origin": request.origin,
            "destination": request.destination,
            "date_from": request.date_from,
            "date_to": request.date_to,
        },
    )
    prices_per_day = prices_per_day_query.all()
    return prices_per_day


def get_day_average_price(
    day_row: Row | Tuple[datetime.date, Decimal, int]
) -> Optional[float]:
    """
    Finds average price for a given day data

    :param day_row: day data row with date, average price and prices amount
    :type day_row: Row | Tuple[datetime.date, Decimal, float]
    :return: returns `None` if day has less than three prices
    and average price of day data otherwise
    :rtype: Optional[float]
    """
    # if day has less than three prices, it's average price should be `null`
    minimal_amount_of_prices_per_day = 3
    average_price = day_row[1]
    prices_count = day_row[2]
    return (
        float(round(average_price, 2))
        if prices_count >= minimal_amount_of_prices_per_day
        else None
    )


def process_prices(
    prices: Sequence[Row] | Sequence[Tuple[datetime.date, Decimal, int]],
) -> AveragePrices:
    """
    Processes prices and returns list of average prices for each day in
    given time period

    :param prices: sequence of prices for given time period
    :type prices: Sequence[Row] | Sequence[Tuple[datetime.date, Decimal, int]]
    :return: list of average prices for each day in given time period
    :rtype: AveragePrices
    """
    result = []

    for price in prices:
        result.append(
            AveragePrice(
                day=str(price[0]),
                average_price=get_day_average_price(price),
            )
        )

    return result
