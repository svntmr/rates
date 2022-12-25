from inspect import signature
from typing import Callable, List, Optional, Type, TypeAlias

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError, validator
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


class AveragePrice(BaseModel):
    day: str
    average_price: Optional[float]


AveragePrices: TypeAlias = List[AveragePrice]
