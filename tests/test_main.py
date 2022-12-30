from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from rates.app.models import AveragePrice, RatesRequest
from rates.main import app


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
                "date_from": "2022-7-1 09:26:03.478039",  # date with minutes
                "date_to": "2022",  # date without month and day
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
                    "msg": "date should be in `%Y-%m-%d` (2020-10-10) format, got "
                    "'2022-7-1 09:26:03.478039'",
                    "type": "value_error",
                },
                {
                    "loc": ["query", "date_to"],
                    "msg": "date should be in `%Y-%m-%d` (2020-10-10) format, "
                    "got '2022'",
                    "type": "value_error",
                },
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
            get_average_prices_patch.assert_called_once_with(
                RatesRequest(
                    date_from="2022-07-01",
                    date_to="2022-07-02",
                    origin="some_origin",
                    destination="some_destination",
                )
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == [{"day": "2022-07-01", "average_price": 4.2}]
