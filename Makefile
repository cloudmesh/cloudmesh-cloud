all: doc

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
