all: doc


doc-help:
	mkdir -p documentation/source/manual
	cms help > documentation/source/manual/commands.rst
	cms help admin > documentation/source/manual/admin.rst
	cms help banner > documentation/source/manual/banner.rst
	cms help clear > documentation/source/manual/clear.rst
	cms help echo > documentation/source/manual/echo.rst
	cms help default > documentation/source/manual/default.rst
	cms help info > documentation/source/manual/info.rst
	cms help pause > documentation/source/manual/pause.rst
	cms help plugin > documentation/source/manual/plugin.rst
	cms help q > documentation/source/manual/q.rst
	cms help quit > documentation/source/manual/quit.rst
	cms help shell > documentation/source/manual/shell.rst
	cms help sleep > documentation/source/manual/sleep.rst
	cms help stopwatch > documentation/source/manual/stopwatch.rst
	cms help sys > documentation/source/manual/sys.rst
	cms help var > documentation/source/manual/var.rst
	cms help vbox > documentation/source/manual/vbox.rst
	cms help vcluster > documentation/source/manual/vcluster.rs
	cms help batch > documentation/source/manual/batch.rst
	cms help version > documentation/source/manual/version.rst

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
