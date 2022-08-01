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
from typing import Dict
from copy import deepcopy
from sympy import Symbol

class Geometry(object):
   """Represents the shape-specific parametric geometry of a `SymPart`."""

   # Public attributes ----------------------------------------------------------------------------

   name: str
   """Unique, identifying name of the `Geometry` instance."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str) -> None:
      """Initializes a `Geometry` instance, where `identifier` uniquely identifies the instance."""
      super().__init__()
      self.name = identifier


   # Built-in method implementations --------------------------------------------------------------

   def __repr__(self) -> str:
      output = [key+' = '+str(val)+', ' for key, val in self.__dict__.items() if key != 'name']
      return ''.join(output).strip(' ,')

   def __eq__(self, other: Geometry) -> bool:
      for key, val in self.__dict__.items():
         if key != 'name' and (key not in other.__dict__ or val != getattr(other, key)):
            return False
      return True

   def __copy__(self) -> Geometry:
      copy = self.__class__.__new__(self.__class__)
      copy.__dict__.update(self.__dict__)
      return copy

   def __deepcopy__(self, memo) -> Geometry:
      copy = self.__class__.__new__(self.__class__)
      memo[id(self)] = copy
      for key, val in self.__dict__.items():
         setattr(copy, key, deepcopy(val, memo))
      return copy

   def __imul__(self, value: float) -> Geometry:
      for key, val in self.__dict__.items():
         if key != 'name':
            setattr(self, key, val * value)
      return self

   def __itruediv__(self, value: float) -> Geometry:
      for key, val in self.__dict__.items():
         if key != 'name':
            setattr(self, key, val / value)
      return self


   # Public methods -------------------------------------------------------------------------------

   def clone(self) -> Geometry:
      """Returns an exact clone of this `Geometry` instance."""
      return deepcopy(self)


   def copy_from(self, other: Geometry) -> Geometry:
      """Copies the geometric parameters from another `Geometry` instance into this one.

      The name of this instance will not be changed or overwritten.

      Parameters
      ----------
      other : `Geometry`
         A Geometry object whose attributes should be copied into this instance.

      Returns
      -------
      self : `Geometry`
         The Geometry instance being manipulated.
      """
      for key, val in other.__dict__.items():
         if key != 'name':
            setattr(self, key, val)
      return self


   def set(self, **kwargs) -> Geometry:
      """Sets the underlying geometric parameters to the values specified.

      The keys in the `**kwargs` dictionary will be different for each `SymPart`. If a key is
      missing or its value is `None`, the corresponding geometric property will be treated
      as a symbol.

      Parameters
      ----------
      **kwargs : `Dict`
         A dictionary containing values or symbols for the geometric properties present in this
         Geometry instance.

      Returns
      -------
      self : `Geometry`
         The Geometry instance being manipulated.
      """
      for key in self.__dict__:
         if key != 'name':
            setattr(self, key, kwargs[key] if key in kwargs and kwargs[key] is not None else
                    Symbol(self.name + '_' + key))
      return self


   def clear(self) -> Geometry:
      """Clears all geometric properties to `0.0`.

      Returns
      -------
      self : `Geometry`
         The Geometry instance being manipulated.
      """
      for key in self.__dict__:
         if key != 'name':
            setattr(self, key, 0.0)
      return self


   def as_dict(self) -> Dict[str, float]:
      """Returns the current geometric properties as a dictionary."""
      return { key: val for key, val in self.__dict__.items() if key != 'name' }
