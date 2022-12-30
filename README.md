# rates

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit hooks](https://github.com/svntmr/rates/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/svntmr/rates/actions)
[![Tests](https://github.com/svntmr/rates/actions/workflows/run-tests.yml/badge.svg)](https://github.com/svntmr/rates/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/74734b747fd97c6697b7/maintainability)](https://codeclimate.com/github/svntmr/rates/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/74734b747fd97c6697b7/test_coverage)](https://codeclimate.com/github/svntmr/rates/test_coverage)

## Project description

### API

Project is a small API with `/rates` endpoint that takes required `date_from`, `date_to`, `origin`, `destination` query parameters and returns a list with the average prices for each day on a route between port codes _origin_ and _destination_. If day has no data or if it has less than 3 prices in total, its average price will be `null`.

Both the _origin, destination_ params accept either port codes or region slugs, making it possible to query for average prices per day between geographic groups of ports.

for example, request

```shell
curl "http://127.0.0.1:8000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
```

will return something like this:

```
[
    {
        "day": "2016-01-01",
        "average_price": 1112
    },
    {
        "day": "2016-01-02",
        "average_price": 1112
    },
    {
        "day": "2016-01-03",
        "average_price": null
    },
    ...
]
```

API docs can be found [here](http://localhost:8000/docs)

### Database

Database consists of four tables:

#### Ports

Information about ports, including:

- 5-character port code
- Port name
- Slug describing which region the port belongs to

#### Regions

A hierarchy of regions, including:

- Slug - a machine-readable form of the region name
- The name of the region
- Slug describing which parent region the region belongs to

Note that a region can have both ports and regions as children, and the region
tree does not have a fixed depth.

#### Prices

Individual daily prices between ports, in USD.

- 5-character origin port code
- 5-character destination port code
- The day for which the price is valid
- The price in USD

#### Codes

Region-slug or port code connected to port code.  
Used as "cache" to simplify queries

- region slug/port code
- port code

#### Database setup

- create `.env` file from `.env.example`: `cp .env.example .env`
- create database container: `make setup-database` (builds and starts database container, executes migrations)

After it, database can be accessed on `localhost:5432` with user `postgres` and password `ratestask`  
Don't forget to update port mapping for `database` service if port 5432 is already taken

## Project setup

- old-fashion way:
  - [create venv and install project dependencies](CONTRIBUTING.md#virtual-environment)
  - [install pre-commit hooks](CONTRIBUTING.md#pre-commit-hooks)
  - create `.env` file from `.env.example`: `cp .env.example .env`
  - setup database: `make setup-database`
  - start uvicorn: `make serve` or `uvicorn rates.main:app --reload`
- using docker compose:
  - build images and start containers: `make`
  - stop containers: `make stop`

### TODO

- async driver for database & async queries
- ~~refactor `get_prices_for_request` (described in function)~~
- validation improvement
  - ~~check if dates are in the right order (from > to)~~
  - (maybe) check if dates are in the range of DB dates
  - (maybe) check if origin and destination exists
