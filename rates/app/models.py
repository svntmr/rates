from datetime import datetime
from inspect import signature
from typing import Any, Callable, Dict, List, Optional, Type, TypeAlias

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError, root_validator, validator
from rates.utils.validation import check_date


def make_dependable(cls: Type) -> Callable:
    """
    Functions adds a classmethod which attempts to init the BaseModel
    and handles formatting of any raised ValidationErrors, custom or otherwise.

    Based on https://github.com/tiangolo/fastapi/issues/1474#issuecomment-1160633178.

    Works for endpoints with query params

    usage:
    def fetch(request: Request = Depends(make_dependable(Request))):

    :param cls: pydantic class to use in endpoint description
    :type cls: Type
    :returns: function which fixes pydantic class validation error handling
    :rtype: Callable
    """

    def init_cls_and_handle_errors(*args, **kwargs):
        try:
            signature(init_cls_and_handle_errors).bind(*args, **kwargs)
            return cls(*args, **kwargs)
        except ValidationError as e:
            for error in e.errors():
                error["loc"] = tuple(("query", *error["loc"]))
            raise HTTPException(422, detail=e.errors())

    init_cls_and_handle_errors.__signature__ = signature(  # type: ignore[attr-defined]
        cls
    )
    return init_cls_and_handle_errors


class RatesRequest(BaseModel):
    date_from: str
    date_to: str
    origin: str
    destination: str

    _check_date_from = validator("date_from", allow_reuse=True)(check_date)
    _check_date_to = validator("date_to", allow_reuse=True)(check_date)

    @root_validator(skip_on_failure=True)
    def check_dates_order(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validator to check that `date_from` is less than `date_to`

        :param values: dict with pydantic model values (with other validators applied)
        :type values: Dict[str, Any]
        :return: model values as dict
        :rtype: Dict[str, Any]
        :raises ValueError: if `date_from` is bigger than `date_to`
        """
        # note: `skip_on_failure=True` means that root validator won't be called if any
        # validator fails before it
        # safe to use straight key access as root validators are executed
        # at the last step (after other fields validation)
        date_from = datetime.strptime(values["date_from"], "%Y-%m-%d")
        date_to = datetime.strptime(values["date_to"], "%Y-%m-%d")

        if date_from > date_to:
            raise ValueError(
                f"`date_from` should be before `date_to`, got "
                f"`date_from`: '{date_from.strftime('%Y-%m-%d')}' "
                f"and `date_to`: '{date_to.strftime('%Y-%m-%d')}"
            )
        return values


class AveragePrice(BaseModel):
    day: str
    average_price: Optional[float]


AveragePrices: TypeAlias = List[AveragePrice]
