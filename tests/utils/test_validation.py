from datetime import date

import pytest
from rates.utils.validation import check_date


class TestCheckDate:
    def test_check_date_raises_if_date_is_in_wrong_format(self):
        with pytest.raises(ValueError) as validation_error:
            # given and when (not full date)
            check_date("2022")

        # then
        assert str(validation_error.value) == (
            "date should be in `%Y-%m-%d` (2020-10-10) format, got '2022'"
        )

        with pytest.raises(ValueError) as validation_error:
            # given and when (date with hours, minutes, seconds)
            check_date("2022-07-01 09:26:03.478039")

        # then
        assert str(validation_error.value) == (
            "date should be in `%Y-%m-%d` (2020-10-10) format, got "
            "'2022-07-01 09:26:03.478039'"
        )

    def test_check_date_date_as_string(self):
        # given
        date_string = "2020-7-1"

        # when
        updated_date = check_date(date_string)

        # then
        assert (
            "2020-07-01" == updated_date
        ), "`check_date` should add zero-padded decimal number for month and day"

    def test_check_date_date_as_date_object(self):
        # given
        date_object = date(year=2020, month=7, day=1)

        # when
        updated_date = check_date(date_object)

        # then
        assert (
            "2020-07-01" == updated_date
        ), "`check_date` should return date as a string"
