# ex Makefile
.PHONY: install format lint test sec

install:
	@poetry install
format:
	@blue .
	@isort .
lint:
	@blue . --check
	@isort . --check
	@prospector
test:
	@pytest -v
sec:
	@pip-audit
run:
	@poetry run python -i correct_score/main.py