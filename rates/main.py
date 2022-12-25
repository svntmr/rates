from fastapi import Depends, FastAPI
from rates.app.models import AveragePrices, RatesRequest, make_dependable
from rates.app.prices import get_average_prices

app = FastAPI()


@app.get("/rates", response_model=AveragePrices)
def rates(request: RatesRequest = Depends(make_dependable(RatesRequest))):
    return get_average_prices(request)
