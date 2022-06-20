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
from ...core.Coordinate import Coordinate
from . import GenericShape
from sympy import Symbol
import math

class Cylinder(GenericShape):
   """Model representing a generic parameteric cylinder.

   By default, the cylinder is oriented such that its flat faces are perpendicular to the z-axis:

   ![Cylinder](https://symbench.github.io/SymCAD/images/Cylinder.png)

   The `geometry` of this shape includes the following parameters:

   - `radius`: Radius (in `m`) of the Cylinder
   - `height`: Height or length (in `m`) of the Cylinder along the z-axis

   Note that the above dimensions should be interpreted as if the Cylinder is unrotated. In other
   words, any shape rotation takes place *after* the Cylinder dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric cylinder object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, material_density_kg_m3)
      setattr(self.geometry, 'radius', Symbol(self.name + '_radius'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Cylinder`."""
      height_mm = 1000.0 * params['height']
      radius_mm = 1000.0 * params['radius']
      return Part.makeCylinder(radius_mm, height_mm)


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, radius_m: Union[float, None],
                             height_m: Union[float, None]) -> Cylinder:
      """Sets the physical geometry of the current `Cylinder` object.

      See the `Cylinder` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(radius=radius_m, height=height_m)
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def mass(self) -> float:
      return super().mass

   @property
   def material_volume(self) -> float:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> float:
      return math.pi * self.geometry.radius**2 * self.geometry.height

   @property
   def surface_area(self) -> float:
      return (2.0 * math.pi * self.geometry.radius * self.geometry.height) + \
             (2.0 * math.pi * self.geometry.radius**2)

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      rotation_center = self.static_center_of_placement \
                             if self.static_center_of_placement is not None else \
                        Coordinate('rotation_center', x=0.0, y=0.0, z=0.0)
      unoriented_centroid = (self.geometry.radius - rotation_center.x,
                             0.0 - rotation_center.y,
                             (0.5 * self.geometry.height) - rotation_center.z)
      return self.orientation.rotate_point(rotation_center.as_tuple(), unoriented_centroid)

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.center_of_gravity

   @property
   def unoriented_length(self) -> float:
      return 2.0 * self.geometry.radius

   @property
   def unoriented_width(self) -> float:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> float:
      return self.geometry.height
