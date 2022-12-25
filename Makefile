.DEFAULT_GOAL := run

install:
	pip install -r requirements.txt

pre-commit-check:
	pre-commit run --all-files

run-tests:
	pytest

test-coverage:
	pytest --cov=rates --cov-report xml

build-database:
	docker compose build database

up-database:
	docker compose up database -d

run-migrations:
	alembic upgrade head

stop:
	docker compose stop

setup-database: build-database up-database run-migrations

serve:
	uvicorn rates.main:app --reload

build: build-database build-api

build-api:
	docker compose build api

up:
	docker compose up -d

run: build up run-migrations
