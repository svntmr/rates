import datetime
from decimal import Decimal
from unittest.mock import ANY, MagicMock, patch

from rates.app.models import AveragePrice, RatesRequest
from rates.app.prices import (
    create_period_dates,
    get_average_prices,
    get_day_average_price,
    process_prices,
)


class TestGetAveragePrices:
    def test_get_average_prices_no_prices(self):
        # given
        with patch(
            "rates.app.prices.get_engine", return_value=MagicMock()
        ) as get_engine_patch, patch(
            "rates.app.prices.get_prices_for_request",
            return_value=[],  # ports have no prices
        ) as get_prices_for_request_patch:
            request = RatesRequest(
                date_from="2022-07-01",
                date_to="2022-07-02",
                origin="some_port_1",
                destination="some_port_2",
            )

            # when
            average_prices = get_average_prices(request)

            # then
            # engine should be created
            get_engine_patch.assert_called_once()
            # connection should be created
            get_engine_patch.return_value.connect.assert_called_once()
            get_prices_for_request_patch.assert_called_once_with(ANY, request)
            expected_prices = [
                AveragePrice(day="2022-07-01", average_price=None),
                AveragePrice(day="2022-07-02", average_price=None),
            ]
            assert expected_prices == average_prices, (
                "function should return average prices for each date with  "
                "price equal to None as ports have no prices"
            )

    def test_get_average_prices(self):
        # given
        with patch(
            "rates.app.prices.get_engine", return_value=MagicMock()
        ) as get_engine_patch, patch(
            "rates.app.prices.get_prices_for_request",
            return_value=[
                (datetime.date(2022, 7, 1), Decimal(100), 2),
                (datetime.date(2022, 7, 2), Decimal(200), 4),
            ],
        ) as get_prices_for_request_patch:
            request = RatesRequest(
                date_from="2022-07-01",
                date_to="2022-07-02",
                origin="some_port_1",
                destination="some_port_2",
            )

            # when
            average_prices = get_average_prices(request)

            # then
            # engine should be created
            get_engine_patch.assert_called_once()
            # connection should be created
            get_engine_patch.return_value.connect.assert_called_once()
            get_prices_for_request_patch.assert_called_once_with(ANY, request)
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


class TestCreatePeriodDates:
    def test_create_period_dates(self):
        expected_period_dates = [
            "2022-07-01",
            "2022-07-02",
            "2022-07-03",
            "2022-07-04",
        ]

        period_dates = create_period_dates("2022-07-01", "2022-07-04")

        assert expected_period_dates == period_dates


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

        processed_prices = process_prices(prices, "2022-07-01", "2022-07-02")

        assert processed_prices == expected_processed_prices

    def test_process_prices_wider_range(self):
        prices = [
            (datetime.date(2022, 7, 1), Decimal(100), 2),
            (datetime.date(2022, 7, 2), Decimal(1111.91), 3),
        ]

        expected_processed_prices = [
            AveragePrice(day="2022-07-01", average_price=None),
            AveragePrice(day="2022-07-02", average_price=1111.91),
            AveragePrice(day="2022-07-03", average_price=None),
            AveragePrice(day="2022-07-04", average_price=None),
        ]

        processed_prices = process_prices(prices, "2022-07-01", "2022-07-04")

        assert processed_prices == expected_processed_prices
