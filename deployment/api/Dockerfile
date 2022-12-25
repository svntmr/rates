FROM python:3.10-slim-buster

WORKDIR /code

COPY ./requirements-core.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./rates /code/rates

CMD ["uvicorn", "rates.main:app", "--host", "0.0.0.0", "--port", "80"]
