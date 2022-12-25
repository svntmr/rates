# rates

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit hooks](https://github.com/svntmr/rates/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/svntmr/rates/actions)
[![Tests](https://github.com/svntmr/rates/actions/workflows/run-tests.yml/badge.svg)](https://github.com/svntmr/rates/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/74734b747fd97c6697b7/maintainability)](https://codeclimate.com/github/svntmr/rates/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/74734b747fd97c6697b7/test_coverage)](https://codeclimate.com/github/svntmr/rates/test_coverage)

## Project description

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
