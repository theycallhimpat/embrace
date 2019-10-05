init:
	pipenv install --dev

test:
	pipenv run pytest

black:
	pipenv run black embrace/ tests/
