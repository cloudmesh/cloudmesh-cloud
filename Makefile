all: doc

doc:
	rm -rf docs
	mkdir -p dest
	cd documentation; make html
	cp -r documentation/build/html/ docs
