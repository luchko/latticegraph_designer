#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 02:24:06 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

setup latticegraph_designer package in your environment
    
"""
from setuptools import setup, find_packages
import os
import pip

import latticegraph_designer

#with open(os.path.abspath('README.rst'), encoding='utf-8') as f:
#    long_description = f.read()


long_description = '''
Lattice graph designer 
***********************

.. image:: https://img.shields.io/pypi/v/latticegraph_designer.svg
        :target: https://pypi.python.org/pypi/latticegraph-designer
        :alt: PyPi

.. image:: https://img.shields.io/pypi/status/latticegraph-designer.svg
        :target: https://pypi.python.org/pypi/latticegraph-designer
        :alt: status

.. image:: https://img.shields.io/pypi/l/latticegraph_designer.svg
        :target: https://github.com/luchko/latticegraph_designer/blob/master/LICENSE.txt
        :alt: License

.. image:: https://readthedocs.org/projects/latticegraph-designer/badge/?version=latest
        :target: http://latticegraph-designer.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
	
Lattice graph designer is a tool which allows to visualize and create a lattice graph model using the intuitive GUI and interactive 3D drag-and-drop graph manipulation pane. It was primarily created for the `ALPS project <http://alps.comp-phys.org/>`_ to deal with a lattice graph of the `Heisenberg model <https://en.wikipedia.org/wiki/Heisenberg_model_(quantum)>`_ defined in `ALPS xml graph format <http://alps.comp-phys.org/mediawiki/index.php/Tutorials:LatticeHOWTO>`_. Support of the other formats and projects can be extended.

- Git-hub repo: https://github.com/luchko/latticegraph_designer
- Documentation: https://latticegraph-designer.readthedocs.io

GUI is based on `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_. Program is compatible with Python 2.7 or Python 3.3+ and PyQt4 4.6+ or PyQt5 5.2+.

Features
========

- import and visualisation of the lattice graph saved in the `ALPS compatible lattice graph xml format  <http://alps.comp-phys.org/mediawiki/index.php/Tutorials:LatticeHOWTO>`_.
- import the crystal structure providing the unit cell parameters, sites coordinates and the space group symmetry operations.
- import the crystal structure from the `CIF file <https://en.wikipedia.org/wiki/Crystallographic_Information_File>`_.
- export the lattice graph to the ALPS compatible xml file.
- interactive 3D drag-and-drop graph manipulation pane based on `matplotlib <http://matplotlib.org/>`_
- manipulation edges (add, remove, change type) referring to the distance between vertices they connect.
- xml code editor (highlighting, synchronization with manipulation pane)
- exporting the figure of the lattice graph model.
- `animation manager <https://github.com/luchko/mpl_animationmanager>`_ allows to animate a 3D model and save the animation in mp4 or gif format.
- preferences manager allows setting the visual theme of the lattice graph displayed on the manipulation pane.

'''

# get list of dependencies from requirements.txt file
with open(os.path.abspath('requirements.txt')) as f:
    install_requires = [p for p in f.read().splitlines() if p != '']

pip.main(['install', 'numpy'])
## trick required to install numpy
#for package in install_requires:
#    pip.main(['install', package])

#import matplotlib.pyplot

setup(
    name='latticegraph_designer',
    version=latticegraph_designer.__version__,
    description='PyQt based GUI tool which allows to visualize, design and export the lattice graph models.',
    long_description=long_description,
    url='https://github.com/luchko/latticegraph_designer',
    author='Ivan Luchko',
    author_email='luchko.ivan@gmail.com',
    documentation='https://latticegraph-designer.readthedocs.io',
    license='MIT',
    packages=['latticegraph_designer', 
              'latticegraph_designer.app',
              'latticegraph_designer.widgets', 
              'latticegraph_designer.test', 
              'mpl_animationmanager'],
    scripts=['scripts/graphdesigner'],
    install_requires=install_requires,
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    test_suite='latticegraph_designer.test',
    keywords='physics material-science graph-visualization crystal-structure lattice alps-project gui',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English'
        ],
    extras_require={
        'testing': ['unittest'],
    }
)
