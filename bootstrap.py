#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Licensed under the terms of the MIT License

"""
Bootstrapping Lattice graph designer

Detect environment and execute program from source

@author: Ivan Luchko (luchko.ivan@gmail.com)  
"""

if __name__ == '__main__':
    import sys
    from latticegraph_designer.app import main

    sys.exit(main.run())
