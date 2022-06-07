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

from __future__ import annotations
from typing import Tuple, Union
from sympy import Expr, Symbol


class Coordinate(object):
   """Represents a set of XYZ Cartesian coordinates."""

   # Public attributes ----------------------------------------------------------------------------

   name: str
   """Unique, identifying name of the `Coordinate` instance."""

   x: Union[float, Expr]
   """X-axis coordinate in meters."""

   y: Union[float, Expr]
   """Y-axis coordinate in meters."""

   z: Union[float, Expr]
   """Z-axis coordinate in meters."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, **kwargs) -> None:
      """Initializes a `Coordinate` instance, where `identifier` uniquely identifies the instance,
      and `**kwargs` may contain the keywords `x`, `y`, or `z` to specify a concrete value
      for each axis of the coordinate. If any of these keywords are missing, the corresponding
      coordinate will be treated as a symbol.
      """
      self.name = identifier
      self.x = kwargs.get('x', Symbol(identifier + '_x'))
      self.y = kwargs.get('y', Symbol(identifier + '_y'))
      self.z = kwargs.get('z', Symbol(identifier + '_z'))


   # Built-in method implementations --------------------------------------------------------------

   def __repr__(self) -> str:
      return 'x = {} m, y = {} m, z = {} m'.format(self.x, self.y, self.z)

   def __eq__(self, other: Coordinate) -> bool:
      return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)


   # Public methods -------------------------------------------------------------------------------

   def clone(self) -> Coordinate:
      """Returns an exact clone of this `Coordinate` instance."""
      return Coordinate(self.name, x=self.x, y=self.y, z=self.z)


   def copy_from(self, other: Coordinate) -> Coordinate:
      """Copies the coordinates from another `Coordinate` instance into this one.

      The name of this instance will not be changed or overwritten.

      Parameters
      ----------
      other : `Coordinate`
         A Coordinate object whose contents should be copied into this instance.

      Returns
      -------
      self : `Coordinate`
         The Coordinate instance being manipulated.
      """
      self.x = other.x
      self.y = other.y
      self.z = other.z
      return self


   def set(self, *, x: Union[float, Expr, None],
                    y: Union[float, Expr, None],
                    z: Union[float, Expr, None]) -> Coordinate:
      """Sets the Cartesian coordinates to the specified values.

      Parameters
      ----------
      x : `Union[float, sympy.Expr, None]`
         Desired x-axis coordinate in meters. If `None` is specified, the coordinate
         will be treated as a symbol.
      y : `Union[float, sympy.Expr, None]`
         Desired y-axis coordinate in meters. If `None` is specified, the coordinate
         will be treated as a symbol.
      z : `Union[float, sympy.Expr, None]`
         Desired z-axis coordinate in meters. If `None` is specified, the coordinate
         will be treated as a symbol.

      Returns
      -------
      self : `Coordinate`
         The Coordinate instance being manipulated.
      """
      self.x = x if x is not None else Symbol(self.name + '_x')
      self.y = y if y is not None else Symbol(self.name + '_y')
      self.z = z if z is not None else Symbol(self.name + '_z')
      return self


   def clear(self) -> Coordinate:
      """Clears all coordinates to `<0, 0, 0>`.

      Returns
      -------
      self : `Coordinate`
         The Coordinate instance being manipulated.
      """
      self.x = self.y = self.z = 0.0
      return self


   def as_tuple(self) -> Tuple[float, float, float]:
      """Returns the current XYZ coordinates as a `tuple`."""
      return self.x, self.y, self.z
