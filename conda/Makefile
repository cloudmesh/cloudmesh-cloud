PACKAGE=conda

conda-build:
    conda-build $(PACKAGE)

conda-install:
    conda install --use-local $(PACKAGE)

conda-all:
    conda convert --platform all ~/anaconda/conda-bld/linux-64/$(PACKAGE)-0.13.1-py27_0.tar.bz2 -o outputdir/

conda-upload:
    anaconda login
    anaconda upload ~/miniconda/conda-bld/linux-64/pyinstrument-0.12-py27_0.tar.bz

#location of file:
#~/anaconda/conda-bld/linux-64/$(PACKAGE)-0.13.1-py27_0.tar.bz2

conda-init:
    conda create -n CONDA python=3.7.1