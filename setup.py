#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 02:24:06 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

setup latticegraph_designer package in your environment
    
"""
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys


import latticegraph_designer
import mpl_animationmanager


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

with open(os.path.abspath('README.rst'), encoding='utf-8') as f:
    long_description = f.read()

class UnitTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import unittest
        errcode = unittest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='latticegraph_designer',
    version=latticegraph_designer.__version__,
    description='PyQt based GUI tool which allows to visualize, design and export the lattice graph models.',
    long_description=long_description,
    url='https://github.com/luchko/latticegraph_designer',
    author='Ivan Luchko',
    author_email='luchko.ivan@gmail.com',
    license='MIT',
    packages=['latticegraph_designer', 'mpl_animationmanager'],
    install_requires=['Flask>=0.10.1',
                    'Flask-SQLAlchemy>=1.0',
                    'SQLAlchemy==0.8.2',
                    ],
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    tests_require=['unittest'],
    cmdclass={'test': UnitTest},
    test_suite='test.test_designer',
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