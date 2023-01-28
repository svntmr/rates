from datetime import date
from inspect import signature
from typing import Any, Callable, Dict, List, Optional, Type, TypeAlias

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    ConstrainedStr,
    Field,
    ValidationError,
    root_validator,
)


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


class PortOrRegion(ConstrainedStr):
    strip_whitespace: bool = True
    min_length: int = 1


class RatesRequest(BaseModel):
    date_from: date = Field(..., description="date period start", example="2016-01-01")
    date_to: date = Field(..., description="date period end", example="2016-01-10")
    origin: PortOrRegion = Field(
        ..., description="region name or port code for origin", example="CNSGH"
    )
    destination: PortOrRegion = Field(
        ...,
        description="region name or port code for destination",
        example="north_europe_main",
    )

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
        date_from = values["date_from"]
        date_to = values["date_to"]

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
