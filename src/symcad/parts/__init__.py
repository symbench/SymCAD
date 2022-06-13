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
This module provides a namespace for the built-in parts and shapes of the SymCAD library.

The `symcad.parts` module should not be imported directly; rather, its subclasses (and
sub-subclasses) should be used as base classes for different types of `symcad.core.SymPart`. A
concrete SymCAD part may be imported from the module corresponding to its type, or it may be
imported directly from the `symcad.parts` module like so:

  - Type-Based: `from symcad.parts.endcaps import FlangedFlatPlate`
  - Direct: `from symcad.parts import FlangedFlatPlate`
"""

from .composite import *
from .endcaps import *
from .fairing import *
from .fixed import *
from .generic import *
