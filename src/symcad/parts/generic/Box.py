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
from PyFreeCAD.FreeCAD import FreeCAD, Part
from typing import Dict, Optional, Tuple, Union
from sympy import Expr, Symbol
from . import GenericShape

class Box(GenericShape):
   """Model representing a generic parameteric box.

   By default, the box is oriented such that its length follows the x-axis, its width follows the
   y-axis, and its height follows the z-axis:

   ![Box](https://symbench.github.io/SymCAD/images/Box.png)

   The `geometry` of this shape includes the following parameters:

   - `length`: Outer length (in `m`) of the Box along the x-axis
   - `width`: Outer width (in `m`) of the Box along the y-axis
   - `height`: Outer height (in `m`) of the Box along the z-axis
   - `thickness`: Thickness (in `m`) of the Box

   Note that the above dimensions should be interpreted as if the Box is unrotated. In other
   words, any shape rotation takes place *after* the Box dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric box object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'length', Symbol(self.name + '_length'))
      setattr(self.geometry, 'width', Symbol(self.name + '_width'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Box`."""
      thickness_mm = 1000.0 * params['thickness']
      outer_length_mm = 1000.0 * params['length']
      outer_width_mm = 1000.0 * params['width']
      outer_height_mm = 1000.0 * params['height']
      inner_length_mm = outer_length_mm - (2.0 * thickness_mm)
      inner_width_mm = outer_width_mm - (2.0 * thickness_mm)
      inner_height_mm = outer_height_mm - (2.0 * thickness_mm)
      outer = Part.makeBox(outer_length_mm, outer_width_mm, outer_height_mm)
      if not fully_displace:
         inner = Part.makeBox(inner_length_mm, inner_width_mm, inner_height_mm,
                              FreeCAD.Vector(thickness_mm, thickness_mm, thickness_mm))
         return outer.cut(inner)
      else:
         return outer


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, length_m: Union[float, None],
                             width_m: Union[float, None],
                             height_m: Union[float, None],
                             thickness_m: Union[float, None]) -> Box:
      """Sets the physical geometry of the current `Box` object.

      See the `Box` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(length=length_m, width=width_m, height=height_m, thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'length': (0.0, 2.0),
         'width': (0.0, 2.0),
         'height': (0.0, 2.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= ((self.geometry.length - 2.0*self.geometry.thickness) *
                 (self.geometry.width - 2.0*self.geometry.thickness) *
                 (self.geometry.height - 2.0*self.geometry.thickness))
      return volume

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
