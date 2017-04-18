Lattice graph designer 1.0a1
*****************************

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

.. image:: https://travis-ci.org/luchko/latticegraph_designer.svg?branch=master
        :target: https://travis-ci.org/luchko/latticegraph_designer
        :alt: travis-ci

.. image:: https://coveralls.io/repos/github/luchko/latticegraph_designer/badge.svg?branch=master
	:target: https://coveralls.io/github/luchko/latticegraph_designer?branch=master
        :alt: coveralls
	
Lattice graph designer is a tool which allows to visualize and create a lattice graph model using the intuitive GUI and interactive 3D drag-and-drop graph manipulation pane. It was primarily created for the `ALPS project <http://alps.comp-phys.org/>`_ to deal with a lattice graph of the `Heisenberg model <https://en.wikipedia.org/wiki/Heisenberg_model_(quantum)>`_ defined in `ALPS xml graph format <http://alps.comp-phys.org/mediawiki/index.php/Tutorials:LatticeHOWTO>`_. Support of the other formats and projects can be extended.

- Git-hub repo: https://github.com/luchko/latticegraph_designer
- Documentation: https://latticegraph-designer.readthedocs.io
- Free software: MIT license

GUI is based on `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_. Program is compatible with Python 2.7 or Python 3.3+ and PyQt4 4.6+ or PyQt5 5.2+.

-------------------------

.. figure:: https://github.com/luchko/latticegraph_designer/blob/master/img_scr/demo.gif?raw=true
   :alt: alternate text

-------------------------

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

Dependencies
============

- **Python** 2.7 or 3.3+
- **PyQt4** 4.6+ or **PyQt5** 5.2+ : PyQt4 is recommended.
- **NumPy**
- **Matplotlib**

**Important note**: *Most dependencies listed above are installed automatically, however in some cases you might need to istall them separately (see next section).*

**Install PyQt4 or PyQt5**

- in case you use conda type: ``$ conda install pyqt=4`` (or 5)
- otherwise follow the links `PyQt4 <http://pyqt.sourceforge.net/Docs/PyQt4/installation.html>`_ or `PyQt5 <http://pyqt.sourceforge.net/Docs/PyQt5/installation.html>`_.

**Install all other dependencies**

``$ pip install -r requirements.txt``

or, incase you use ``conda``

``$ conda install --file requirements.txt``
	
Installation and launching
==========================

This section explains how to install and launch the latest stable release of the Lattice graph designer in one of the cross-platform ways listed bellow. If you prefer testing the development version, please use the bootstrap script (see next section).

Installation using ``conda`` `scientific package manager <https://conda.io/docs/index.html>`_ (recommended way)
-----------------------------------------------------------------------------------------------------------------

*PROJECT IS NOT RELEASED YET*

Type in your command prompt:

``$ pip install conda``		(if ``conda`` is not installed yet)

``$ conda install latticegraph_designer``

**Note:** *All dependencies are installed by* ``conda`` *automatically.*

Installation using ``pip`` package manager from `PyPI <https://pypi.python.org/pypi>`_
--------------------------------------------------------------------------------------

*PROJECT IS NOT RELEASED YET*

Type in your command prompt:

``$ pip install latticegraph_designer``

**Important note:** *This also installs all dependencies except PyQt4 or PyQt5. Those have to be installed separately after installing Python.*

Installation from source
------------------------

**Note:** *This is temporary installation way untill the using of* ``conda`` *or* ``pip`` *is not implemented.*

- `Download a source <https://github.com/luchko/latticegraph_designer/archive/master.zip>`_ of the last stable package version.
- Open the terminal and move to the package root directory.
- In your command prompt type:

	``$ python setup.py install``

Launching the program
----------------------

- After completing the installation you can launch the program simply typping in your command prompt:

``$ graphdesigner [pathToYourLatticeGraphFile.xml]``

:note: 
	If ``pathToYourLatticeGraphFile.xml`` is not provided the program will load a default example. 
	You can open a lattice graph file later.

- Optionally you can lock a tool's link on the launcher for quick access.

Running from source
-------------------

The fastest way to run LatticeGraph designer is to follow this steps:

1. Make sure that all dependencies are installed.
2. `Download a source <https://github.com/luchko/latticegraph_designer/archive/master.zip>`_ of the last stable package version.
3. Run ``$ python bootstrap.py`` from the package root directory.

You may want to do this for fixing bugs, adding the new features, learning how the tool works or just getting a taste of it.

Running ``unittest``
--------------------

After making any changes in the source code you can run ``unitittest`` to make sure that nothing is broken by typing in your command prompt:

``$ python setup.py test``

**Note:** *In case ALPS library is installed* ``unitittest`` *also checks for ALPS compatibility of the exported xml lib file using ALPS* ``printgraph`` *tool.*

Contacts
========

About the feature extension or bugs report you can `create the issue or feature request <https://github.com/luchko/latticegraph_designer/issues>`_ or feel free to contact me directly by e-mail:

**Ivan Luchko** - luchko.ivan@gmail.com

Widgets references
==================

* `Matplotlib animation manager <https://github.com/luchko/mpl_animationmanager>`_
* `QCodeEditor <https://github.com/luchko/QCodeEditor>`_
