#!/usr/bin/env bash

sudo apt-get update

# Define the value to download
if [ "$TRAVIS_OS_NAME" = "linux" ]; then
    MINICONDA_OS=$MINICONDA_LINUX;
elif [ "$TRAVIS_OS_NAME" = "osx" ]; then
    MINICONDA_OS=$MINICONDA_OSX;
fi

# You may want to periodically update this, although the conda update
# conda line below will keep everything up-to-date.  We do this
# conditionally because it saves us some downloading if the version is
# the same.
if [ "$TRAVIS_PYTHON_VERSION" = "2.7" ]; then
    wget "http://repo.continuum.io/miniconda/Miniconda-$MINICONDA_VERSION-$MINICONDA_OS.sh" -O miniconda.sh;
else
    wget "http://repo.continuum.io/miniconda/Miniconda3-4.2.12-$MINICONDA_OS.sh" -O miniconda.sh;
fi
    
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
# Useful for debugging any issues with conda
conda info -a

# setup evironment
if [ "${USE_CONDA}" = "true" ]; then
	# configure conda test-environment
#	conda install conda-build=2.1.0;  # needed to build conda
    conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION;
    source activate test-environment;
                
#    conda install latticegraph_designer
  	# we use this temporarly
	conda install pyqt;
	python setup.py install;
else
  	# we still use conda to install pyqt
	conda install pyqt;   
	python setup.py install;	  
fi

# Install alps for printgraph testing
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ]; then
    conda config --add channels conda-forge;
    conda install alps;
fi

conda list
