#!/usr/bin/env python3
# Copyright (C) 2022, Will Hedgecock
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides a namespace for all shared, basic functionality of the SymCAD library.

Public classes within the module include:

- `symcad.core.Assembly`
- `symcad.core.Coordinate`
- `symcad.core.Geometry`
- `symcad.core.Rotation`
- `symcad.core.SymPart`

The `symcad.core` module should not be imported directly; rather, its contained classes should be
imported like so:

`from symcad.core import Coordinate`
"""

from .Coordinate import Coordinate
from .Geometry import Geometry
from .Rotation import Rotation
from .SymPart import SymPart
from .Assembly import Assembly
