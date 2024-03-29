from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from rates.app.models import AveragePrice, RatesRequest
from rates.main import app, engine


class TestRatesEndpoint:
    client: TestClient
    endpoint: str

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        cls.endpoint = "/rates"

    def test_rates_endpoint_fails_on_empty_request(self):
        # given & when
        response = self.client.get(self.endpoint)
        # then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "date_from"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["query", "date_to"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["query", "origin"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["query", "destination"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ]
        }

    def test_rates_endpoint_fails_on_request_with_wrong_date_format(self):
        # given & when
        response = self.client.get(
            self.endpoint,
            params={
                "date_from": "2022-7-1 09:26:03.478039",
                "date_to": "2022-01-10",
                "origin": "some_origin",
                "destination": "some_destination",
            },
        )
        # then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "date_from"],
                    "msg": "invalid date format",
                    "type": "value_error.date",
                }
            ]
        }

        # given & when
        response = self.client.get(
            self.endpoint,
            params={
                "date_from": "2022-01-10",
                "date_to": "2022-7-1 09:26:03.478039",
                "origin": "some_origin",
                "destination": "some_destination",
            },
        )
        # then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "date_to"],
                    "msg": "invalid date format",
                    "type": "value_error.date",
                }
            ]
        }

    def test_rates_endpoint_fails_on_request_with_start_date_bigger_than_end_date(self):
        # given & when
        response = self.client.get(
            self.endpoint,
            params={
                "date_from": "2016-01-11",  # from bigger than to
                "date_to": "2016-01-01",
                "origin": "some_origin",
                "destination": "some_destination",
            },
        )
        # then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "__root__"],
                    "msg": "`date_from` should be before `date_to`, got `date_from`: "
                    "'2016-01-11' and `date_to`: '2016-01-01",
                    "type": "value_error",
                }
            ]
        }

    def test_rates_endpoint_fails_on_request_with_empty_origin_and_destination(self):
        # given & when
        response = self.client.get(
            self.endpoint,
            params={
                "date_from": "2016-01-01",
                "date_to": "2016-01-02",
                "origin": "",
                "destination": "    ",
            },
        )
        # then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "origin"],
                    "msg": "ensure this value has at least 1 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 1},
                },
                {
                    "loc": ["query", "destination"],
                    "msg": "ensure this value has at least 1 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 1},
                },
            ]
        }

    def test_rates_endpoint_calls_get_average_prices(self):
        # given
        with patch(
            "rates.main.get_average_prices",
            return_value=[(AveragePrice(day="2022-07-01", average_price=4.2))],
        ) as get_average_prices_patch:
            # when
            response = self.client.get(
                self.endpoint,
                params={
                    "date_from": "2022-07-01",
                    "date_to": "2022-07-02",
                    "origin": "some_origin",
                    "destination": "some_destination",
                },
            )

            # then
            # `get_average_prices` should be called with engine from `main.py` and
            # provided request
            get_average_prices_patch.assert_called_once_with(
                engine,
                RatesRequest(
                    date_from="2022-07-01",
                    date_to="2022-07-02",
                    origin="some_origin",
                    destination="some_destination",
                ),
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == [{"day": "2022-07-01", "average_price": 4.2}]
