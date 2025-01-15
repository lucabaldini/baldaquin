all:

flake:
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

ruff:
	ruff check .

lint:
	pylint baldaquin \
		--disable too-many-ancestors \
		--disable too-many-arguments \
		--disable too-many-function-args \
		--disable too-many-instance-attributes \
		--disable c-extension-no-member \
		--disable use-dict-literal \
		--disable too-many-positional-arguments \
		--ignore _version.py

test:
	python -m pytest tests -s

html:
	cd docs; make html

clean:
	rm -rf baldaquin/__pycache__ baldaquin/*/__pycache__ tests/__pycache__ .pytest_cache

cleandoc:
	cd docs; make clean

cleanall: clean cleandoc
