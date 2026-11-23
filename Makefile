PY ?= python3

.PHONY: freeze verify report test clean

freeze:
	$(PY) -m ledger freeze

verify:
	$(PY) -m ledger verify

report:
	$(PY) -m ledger report

test:
	$(PY) -m pytest -q

clean:
	rm -rf out .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
