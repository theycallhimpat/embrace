init:
	pipenv install --dev

test:
	pipenv run pytest

black:
	pipenv run black embrace/ tests/

mypy:
	pipenv run mypy --disallow-untyped-defs embrace/ tests/

pylint:
	pipenv run pylint embrace/ tests/
