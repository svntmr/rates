install:
	pip install -r requirements.txt

pre-commit-check:
	pre-commit run --all-files
