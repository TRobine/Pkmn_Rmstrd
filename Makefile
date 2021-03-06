# Copyright pyLHC/OMC-team <pylhc@github.com>

# Documentation for most of what you will see here can be found at the following links:
# for the GNU make special targets: https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
# for python packaging: https://docs.python.org/3/distutils/introduction.html

# ANSI escape sequences for bold, cyan, dark blue, end, pink and red.
B = \033[1m
C = \033[96m
D = \033[34m
E = \033[0m
P = \033[95m
R = \033[31m

.PHONY : help archive clean doc install tests

all: install

help:
	@echo "Please use 'make $(R)<target>$(E)' where $(R)<target>$(E) is one of:"
	@echo "  $(R) clean $(E)          to recursively remove build, run, and bitecode files/dirs."
	@echo "  $(R) format $(E)  \t  to recursively apply PEP8 formatting through the $(P)Black$(E) cli tool."
#	@echo "  $(R) doc $(E)            to build the documentation with `sphinx`."
	@echo "  $(R) install $(E)        to 'pip install' this package into your activated environment."
	@echo "  $(R) tests $(E)          to run tests with the the pytest package."


clean:
	@echo "Cleaning up distutils remains."
	@rm -rf build
	@rm -rf dist
	@rm -rf pokejdr.egg-info
	@rm -rf .eggs
	@echo "Cleaning up bitecode files and python cache."
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@echo "Cleaning up pytest cache."
	@find . -type d -name '*.pytest_cache' -exec rm -rf {} + -o -type f -name '*.pytest_cache' -exec rm -rf {} +
	@echo "Cleaning up mypy cache."
	@find . -type d -name "*.mypy_cache" -exec rm -rf {} +
	@echo "Cleaning up coverage reports."
	@find . -type f -name '.coverage' -exec rm -rf {} + -o -type f -name 'coverage.xml' -delete
	@echo "All cleaned up!\n"

#doc: clean
#	@echo "$(B)Creating documentation build with Sphinx.$(E)"
#	@python -m sphinx -b html doc ./doc_build -d ./doc_build
#	@echo "Done! Documentation source is in the $(C)doc_build/$(E) directory."

format:
	@echo "Sorting imports and formatting code to PEP8, default line length is 100 characters."
	@python -m isort . && python -m black -l 100 .

install: format
	@echo "$(B)Installing this package to your active environment.$(E)"
	@pip install --upgrade .

tests: format clean install
	@python -m pytest --cov=pokejdr --cov-report term-missing
	@make clean

# Catch-all unknow targets without returning an error. This is a POSIX-compliant syntax.
.DEFAULT:
	@echo "Make caught an invalid target! See help output below for available targets."
	@make help