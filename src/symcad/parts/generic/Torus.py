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

class Torus(GenericShape):
   """Model representing a generic parameteric torus.

   By default, the torus is oriented such that the hollow center is perpendicular to the z-axis:

   ![Torus](https://symbench.github.io/SymCAD/images/Torus.png)

   The `geometry` of this shape includes the following parameters:

   - `hole_radius`: Radius (in `m`) of the central hole in the Torus up to and excluding the tube
   - `tube_radius`: Radius (in `m`) of the tube of the Torus

   Note that the above dimensions should be interpreted as if the Torus is unrotated. In other
   words, any shape rotation takes place *after* the Torus dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric torus object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, material_density_kg_m3)
      setattr(self.geometry, 'hole_radius', Symbol(self.name + '_hole_radius'))
      setattr(self.geometry, 'tube_radius', Symbol(self.name + '_tube_radius'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Torus`."""
      hole_radius_mm = 1000.0 * params['hole_radius']
      tube_radius_mm = 1000.0 * params['tube_radius']
      return Part.makeTorus(hole_radius_mm + tube_radius_mm, tube_radius_mm)


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, hole_radius_m: Union[float, None],
                             tube_radius_m: Union[float, None]) -> Torus:
      """Sets the physical geometry of the current `Torus` object.

      See the `Torus` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(hole_radius=hole_radius_m,
                        tube_radius=tube_radius_m)
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
      return (math.pi * self.geometry.tube_radius**2) * \
             (2.0 * math.pi * (self.geometry.hole_radius + self.geometry.tube_radius))

   @property
   def surface_area(self) -> float:
      return (2.0 * math.pi * (self.geometry.hole_radius + self.geometry.tube_radius)) * \
             (2.0 * math.pi * self.geometry.tube_radius)

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      rotation_center = self.static_center_of_placement \
                             if self.static_center_of_placement is not None else \
                        Coordinate('rotation_center', x=0.0, y=0.0, z=0.0)
      unoriented_centroid = ((self.geometry.hole_radius + (2.0 * self.geometry.tube_radius))
                                - rotation_center.x,
                             0.0 - rotation_center.y,
                             self.geometry.tube_radius - rotation_center.z)
      return self.orientation.rotate_point(rotation_center.as_tuple(), unoriented_centroid)

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.center_of_gravity

   @property
   def unoriented_length(self) -> float:
      return (2.0 * self.geometry.hole_radius) + (4.0 * self.geometry.tube_radius)

   @property
   def unoriented_width(self) -> float:
      return (2.0 * self.geometry.hole_radius) + (4.0 * self.geometry.tube_radius)

   @property
   def unoriented_height(self) -> float:
      return 2.0 * self.geometry.tube_radius
