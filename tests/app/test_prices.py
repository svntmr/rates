import datetime
from decimal import Decimal
from unittest.mock import ANY, AsyncMock, patch

import pytest
from rates.app.models import AveragePrice, RatesRequest
from rates.app.prices import (
    get_average_prices,
    get_day_average_price,
    process_prices,
)
from sqlalchemy.engine import Engine


class TestGetAveragePrices:
    @pytest.mark.asyncio
    async def test_get_average_prices(self):
        # given
        with patch(
            "rates.app.prices.get_prices_for_request",
            return_value=[
                (datetime.date(2022, 7, 1), Decimal(100), 2),
                (datetime.date(2022, 7, 2), Decimal(200), 4),
            ],
        ) as get_prices_for_request_patch:
            async_engine_mock = AsyncMock(Engine)

            request = RatesRequest(
                date_from="2022-07-01",
                date_to="2022-07-02",
                origin="some_port_1",
                destination="some_port_2",
            )

            # when
            average_prices = await get_average_prices(async_engine_mock, request)

            # then
            # connection should be created
            async_engine_mock.connect.assert_called_once()
            # get_prices_for_request should be called with connection and request
            get_prices_for_request_patch.assert_awaited_once_with(ANY, request)
            expected_prices = [
                AveragePrice(  # day has less than three prices
                    day="2022-07-01", average_price=None
                ),
                AveragePrice(day="2022-07-02", average_price=200.0),
            ]
            assert expected_prices == average_prices


class TestGetDayAveragePrice:
    def test_get_day_average_price(self):
        assert (
            get_day_average_price((datetime.date(2022, 7, 1), Decimal(100), 2)) is None
        ), "average price for row with less than three prices should be None"
        assert 175.53 == get_day_average_price(
            (datetime.date(2022, 7, 1), Decimal(175.5345), 3)
        ), "average price for row with three prices should be average price from row"
        assert 150.0 == get_day_average_price(
            (datetime.date(2022, 7, 1), Decimal(150), 4)
        ), (
            "average price for row with more than three prices should be"
            "average price from row"
        )


class TestProcessPrices:
    def test_process_prices(self):
        prices = [
            (datetime.date(2022, 7, 1), Decimal(100), 2),
            (datetime.date(2022, 7, 2), Decimal(1111.91), 3),
        ]

        expected_processed_prices = [
            AveragePrice(day="2022-07-01", average_price=None),
            AveragePrice(day="2022-07-02", average_price=1111.91),
        ]

        processed_prices = process_prices(prices)

        assert processed_prices == expected_processed_prices
