all: doc


manual:
	mkdir -p documentation/source/manual
	cms help > /tmp/commands.rst
	echo "Commands" > documentation/source/manual/commands.rst
	echo "========" >> documentation/source/manual/commands.rst
	echo  >> documentation/source/manual/commands.rst
	tail -n +4 /tmp/commands.rst >> documentation/source/manual/commands.rst
	cms man --kind=rst admin > documentation/source/manual/admin.rst
	cms man --kind=rst banner > documentation/source/manual/banner.rst
	cms man --kind=rst clear > documentation/source/manual/clear.rst
	cms man --kind=rst echo > documentation/source/manual/echo.rst
	cms man --kind=rst default > documentation/source/manual/default.rst
	cms man --kind=rst info > documentation/source/manual/info.rst
	cms man --kind=rst pause > documentation/source/manual/pause.rst
	cms man --kind=rst plugin > documentation/source/manual/plugin.rst
	cms man --kind=rst q > documentation/source/manual/q.rst
	cms man --kind=rst quit > documentation/source/manual/quit.rst
	cms man --kind=rst shell > documentation/source/manual/shell.rst
	cms man --kind=rst sleep > documentation/source/manual/sleep.rst
	cms man --kind=rst stopwatch > documentation/source/manual/stopwatch.rst
	cms man --kind=rst sys > documentation/source/manual/sys.rst
	cms man --kind=rst var > documentation/source/manual/var.rst
	cms man --kind=rst vbox > documentation/source/manual/vbox.rst
	cms man --kind=rst vcluster > documentation/source/manual/vcluster.rst
	cms man --kind=rst batch > documentation/source/manual/batch.rst
	cms man --kind=rst version > documentation/source/manual/version.rst
	cms man --kind=rst open > documentation/source/manual/open.rst
	cms man --kind=rst vm > documentation/source/manual/vm.rst
	cms man --kind=rst network > documentation/source/manual/network.rst
	cms man --kind=rst key > documentation/source/manual/key.rst
	cms man --kind=rst secgroup > documentation/source/manual/secgroup.rst
	cms man --kind=rst image > documentation/source/manual/image.rst
	cms man --kind=rst flavor > documentation/source/manual/flavor.rst
	cms man --kind=rst ssh > documentation/source/manual/ssh.rst
	cms man --kind=rst storage > documentation/source/manual/storage.rst
	cms man --kind=rst workflow > documentation/source/manual/workflow.rst


doc:
	rm -rf docs
	mkdir -p dest
	cd documentation; make html
	cp -r documentation/build/html/ docs

view:
	open docs/index.html

nist-install: nist-download nist-copy

nist-download:
	rm -rf ../nist
	git clone https://github.com/davidmdem/nist ../nist


nist-copy:
	cd cm4/api; rm -rf specs; mkdir specs;
	rsync -a --prune-empty-dirs --include '*/' --include '*.yaml' --exclude '*' ../nist/services/ ./cm4/api/specs/


#
# TODO: BUG: This is broken
#
#pylint:
#	mkdir -p docs/qc/pylint/cm
#	pylint --output-format=html cloudmesh > docs/qc/pylint/cm/cloudmesh.html
#	pylint --output-format=html cm4 > docs/qc/pylint/cm/cm4.html

######################################################################
# PYPI
######################################################################


twine:
	pip install -U twine

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

patch: clean
	$(call banner, patch to testpypi)
	bumpversion --allow-dirty patch
	python setup.py sdist bdist_wheel
	git push origin master --tags
	twine check dist/*
	twine upload --repository testpypi https://test.pypi.org/legacy/ dist/*

release: clean dist
	$(call banner, release to pypi)
	bumpversion release
	python setup.py sdist bdist_wheel
	git push origin master --tags
	twine check dist/*
	twine upload dist/*

pip: patch
	pip install --index-url https://test.pypi.org/simple/ \
	    --extra-index-url https://pypi.org/simple cloudmesh-$(package)

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push