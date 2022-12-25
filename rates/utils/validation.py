from datetime import datetime
from typing import Any


def check_date(v: Any) -> Any:
    """
    Checks if provided value is date string in the expected `%Y-%m-%d` format
    Used as validator in pydantic model

    :param v: value
    :type v: Any
    :return: returns string with date in the right format
    :rtype: Any
    :raises ValueError: if value is not date or date is in wrong format
    """
    try:
        if not isinstance(v, str):
            v = str(v)
        v = datetime.strptime(v, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as value_error:
        raise ValueError(
            f"date should be in `%Y-%m-%d` (2020-10-10) format, got '{v}'"
        ) from value_error
    return v
