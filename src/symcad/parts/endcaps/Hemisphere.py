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
from . import EndcapShape
import math

class Hemisphere(EndcapShape):
   """Model representing a hollow, parametric, hemispherical endcap.

   By default, the endcap is oriented such that its base is perpendicular to the z-axis:

   ![Hemisphere](https://symbench.github.io/SymCAD/images/Hemisphere.png)

   The `geometry` of this shape includes the following parameters:

   - `radius`: Radius (in `m`) of the Hemisphere
   - `thickness`: Thickness (in `m`) of the shell of the Hemisphere

   Note that the above dimensions should be interpreted as if the Hemisphere is unrotated.
   In other words, any shape rotation takes place *after* the Hemisphere dimensions have been
   specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a hollow, parametric, hemispherical endcap object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'radius', Symbol(self.name + '_radius'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Hemisphere`."""
      thickness_mm = 1000.0 * params['thickness']
      outer_radius_mm = 1000.0 * params['radius']
      inner_radius_mm = outer_radius_mm - thickness_mm
      outer = Part.makeSphere(outer_radius_mm, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 0, 90, 360)
      if not fully_displace:
         inner = Part.makeSphere(inner_radius_mm, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 0, 90, 360)
         return outer.cut(inner)
      else:
         return outer


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, radius_m: Union[float, None],
                             thickness_m: Union[float, None]) -> Hemisphere:
      """Sets the physical geometry of the current `Hemisphere` object.

      See the `Hemisphere` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(radius=radius_m, thickness=thickness_m)
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= ((2.0 * math.pi / 3.0) * (self.geometry.radius - self.geometry.thickness)**3)
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return (2.0 * math.pi / 3.0) * self.geometry.radius**3

   @property
   def surface_area(self) -> Union[float, Expr]:
      return 2.0 * math.pi * self.geometry.radius**2

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return self.geometry.radius, self.geometry.radius, 0.5 * self.geometry.radius

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.geometry.radius, self.geometry.radius, 3.0 * self.geometry.radius / 8.0

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.radius
