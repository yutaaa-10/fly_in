PYTHON := python3
MAP ?= maps/easy/01_linear_path.txt

install:
	@$(PYTHON) -m pip install flake8 mypy

run:
	@$(PYTHON) main.py $(MAP)

debug:
	@$(PYTHON) -m pdb main.py $(MAP)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

.PHONY: install run debug clean lint lint-strict