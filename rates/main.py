from fastapi import Depends, FastAPI
from rates.app.models import AveragePrices, RatesRequest, make_dependable
from rates.app.prices import get_average_prices
from rates.database.engine import get_engine

app = FastAPI()
engine = get_engine()


@app.get("/rates", response_model=AveragePrices)
async def rates(request: RatesRequest = Depends(make_dependable(RatesRequest))):
    return await get_average_prices(engine, request)
