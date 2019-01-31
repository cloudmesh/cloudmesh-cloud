all: doc


manual:
	mkdir -p documentation/source/manual
	cms help > documentation/source/manual/commands.rst
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
	cms man --kind=rst vcluster > documentation/source/manual/vcluster.rs
	cms man --kind=rst batch > documentation/source/manual/batch.rst
	cms man --kind=rst version > documentation/source/manual/version.rst


doc:
	rm -rf docs
	mkdir -p dest
	cp README.md documentation/source
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
