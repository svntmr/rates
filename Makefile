install:
	pip install -r requirements.txt

pre-commit-check:
	pre-commit run --all-files

run-tests:
	pytest

test-coverage:
	pytest --cov=rates --cov-report xml
