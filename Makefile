PYTHON := python3
MAP ?= maps/easy/01_linear_path.txt

install:
	@$(PYTHON) -m pip install flake8 mypy pygame

run:
	@$(PYTHON) main.py $(MAP)

debug:
	@$(PYTHON) -m pdb main.py $(MAP)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	$(PYTHON) -m flake8 application.py graph.py main.py models.py parser_helper.py \
		parser.py pathfinder.py router.py simulator.py visualizer.py
	$(PYTHON) -m mypy application.py graph.py main.py models.py parser_helper.py \
		parser.py pathfinder.py router.py simulator.py visualizer.py \
		--warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 application.py graph.py main.py models.py parser_helper.py \
	                    parser.py pathfinder.py router.py simulator.py visualizer.py
	$(PYTHON) -m mypy application.py graph.py main.py models.py parser_helper.py \
	                        parser.py pathfinder.py router.py simulator.py visualizer.py --strict

.PHONY: install run debug clean lint lint-strict
