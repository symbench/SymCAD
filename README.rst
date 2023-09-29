SymCAD Library
==============

Getting Started
---------------

Full documentation for the SymCAD library can be found at https://symbench.github.io/SymCAD


Installation
------------

The SymCAD library may be installed via pip using:

``python3 -m pip install git+https://github.com/symbench/SymCAD``

Alternately, for development purposes, the package may be cloned and installed from the root ``SymCAD`` directory by calling:

``python3 -m pip install -e .``

Note, if you are not developing this package, omit the ``-e`` flag.


Testing
-------

Tests are individual scripts located in the ``tests`` directory that are expected to run without error.
For example:

::

   cd SymCAD
   python3 tests/parts/generic/test_cuboid.py


Known TODO Items
----------------

- Add docs for custom parts - auto-retrieval of free params
- Fix Cg/Cg/Props for some endcaps
