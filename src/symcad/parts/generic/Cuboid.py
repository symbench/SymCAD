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
from PyFreeCAD.FreeCAD import Part
from typing import Dict, Optional, Tuple, Union
from sympy import Expr, Symbol
from . import GenericShape

class Cuboid(GenericShape):
   """Model representing a generic parameteric cuboid.

   By default, the cuboid is oriented such that its length follows the x-axis, its width follows
   the y-axis, and its height follows the z-axis:

   ![Cuboid](https://symbench.github.io/SymCAD/images/Cuboid.png)

   The `geometry` of this shape includes the following parameters:

   - `length`: Length (in `m`) of the Cuboid along the x-axis
   - `width`: Width (in `m`) of the Cuboid along the y-axis
   - `height`: Height (in `m`) of the Cuboid along the z-axis

   Note that the above dimensions should be interpreted as if the Cuboid is unrotated. In other
   words, any shape rotation takes place *after* the Cuboid dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric cuboid object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, material_density_kg_m3)
      setattr(self.geometry, 'length', Symbol(self.name + '_length'))
      setattr(self.geometry, 'width', Symbol(self.name + '_width'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Cuboid`."""
      length_mm = 1000.0 * params['length']
      width_mm = 1000.0 * params['width']
      height_mm = 1000.0 * params['height']
      return Part.makeBox(length_mm, width_mm, height_mm)


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, length_m: Union[float, None],
                             width_m: Union[float, None],
                             height_m: Union[float, None]) -> Cuboid:
      """Sets the physical geometry of the current `Cuboid` object.

      See the `Cuboid` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(length=length_m, width=width_m, height=height_m)
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return self.geometry.length * self.geometry.width * self.geometry.height

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (2.0 * self.geometry.length * self.geometry.width) + \
             (2.0 * self.geometry.length * self.geometry.height) + \
             (2.0 * self.geometry.width * self.geometry.height)

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (0.5 * self.geometry.length,
              0.5 * self.geometry.width,
              0.5 * self.geometry.height)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.geometry.width

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height
