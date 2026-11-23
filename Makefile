PY ?= python3

.PHONY: freeze verify report test clean

freeze:
	uv run --quiet --group freeze python -m ledger freeze

verify:
	$(PY) -m ledger verify

report:
	$(PY) -m ledger report

test:
	uv run --quiet --with pytest pytest

clean:
	rm -rf out .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
