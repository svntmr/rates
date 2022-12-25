import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from rates.app.models import AveragePrice, AveragePrices, RatesRequest
from rates.database.engine import get_engine
from sqlalchemy import text
from sqlalchemy.engine import Connection, Row


def get_average_prices(request: RatesRequest) -> AveragePrices:
    """
    Finds average prices for given origin, destination and date range

    :param request: request with origin, destination and date range
    :type request: RatesRequest
    :return: list of average prices for each day in date range
    :rtype: AveragePrices
    """
    date_from = request.date_from
    date_to = request.date_to

    engine = get_engine()
    with engine.connect() as connection:
        prices = get_prices_for_request(connection, request)

    return process_prices(prices, date_from, date_to)


def get_prices_for_request(connection: Connection, request: RatesRequest) -> List[Row]:
    """
    Fetches day, average prices and prices amount for given ports and dates

    :param connection: sqlalchemy connection instance
    :type connection: Connection
    :param request: request with origin, destination and date range
    :type request: RatesRequest
    :return: list of rows with day, average prices and prices amount
    :rtype: List[Row]
    """
    # option for refactoring: https://stackoverflow.com/a/62414835
    # will allow to get rid of `create_period_dates` and simplify `process_prices`
    prices_per_day = connection.execute(
        text(
            "SELECT day, avg(price) AS avg_price, count(price) AS prices_count "
            "FROM prices "
            "JOIN (SELECT code FROM codes WHERE key = :origin) origin_codes "
            "ON prices.orig_code = origin_codes.code "
            "JOIN (SELECT code FROM codes WHERE key = :destination) "
            "destination_codes ON prices.dest_code = destination_codes.code "
            "WHERE day BETWEEN :date_from and :date_to "
            "GROUP BY day "
            "ORDER BY day "
        ),
        {
            "origin": request.origin,
            "destination": request.destination,
            "date_from": request.date_from,
            "date_to": request.date_to,
        },
    ).all()
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


def create_period_dates(date_from: str, date_to: str) -> List[str]:
    """
    Creates dates for given time period

    :param date_from: start of time period
    :type date_from: str
    :param date_to: end of time period
    :type date_to: str
    :return: list of dates for given time period
    :rtype: List[str]
    """
    period_start = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
    period_end = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
    period_dates = [
        str(period_start + datetime.timedelta(days=x))
        for x in range((period_end - period_start).days + 1)
    ]
    return period_dates


def process_prices(
    prices: List[Row] | List[Tuple[datetime.date, Decimal, int]],
    date_from: str,
    date_to: str,
) -> AveragePrices:
    """
    Processes prices and returns list of average prices for each day in
    given time period

    :param prices: list of prices for given time period
    :type prices: List[Row] | List[Tuple[datetime.date, Decimal, int]]
    :param date_from: start of time period
    :type date_from: str
    :param date_to: end of time period
    :type date_to: str
    :return: list of average prices for each day in given time period
    :rtype: AveragePrices
    """
    period_dates = create_period_dates(date_from, date_to)

    found_prices_per_day = {
        str(price[0]): AveragePrice(
            day=str(price[0]),
            average_price=get_day_average_price(price),
        )
        for price in prices
    }

    result = []
    for date in period_dates:
        if str(date) in found_prices_per_day:
            result.append(found_prices_per_day[str(date)])
        else:
            result.append(
                AveragePrice(
                    day=str(date),
                    average_price=None,
                )
            )

    return result
