#
# PyLucid Makefile
# ~~~~~~~~~~~~~~~~
#
# Shortcuts for various tasks.

check-release: clean pylint documentation

release: documentation
	@(python2.4 setup.py release bdist_egg upload; python2.5 setup.py release bdist_egg sdist upload)
#TODO: do we need a egg for python 2.3?

clean: clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

#test:
#	@(cd tests; py.test $(TESTS))
#TODO: uncomment if we realy have some good unit tests

pylint:
	@pylint --rcfile scripts/pylintrc PyLucid
