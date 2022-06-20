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
from sympy import Symbol, sqrt
import math

class Cone(GenericShape):
   """Model representing a generic parameteric cone.

   By default, the cone is oriented such that its base is perpendicular to the z-axis:

   ![Cone](https://symbench.github.io/SymCAD/images/Cone.png)

   The `geometry` of this shape includes the following parameters:

   - `bottom_radius`: Radius (in `m`) of the base of the Cone (must be larger than `top_radius`)
   - `top_radius`: Radius (in `m`) of the truncated Cone tip (may be `0` to create a full Cone)
   - `height`: Height (in `m`) of the Cone from base to tip

   If a non-truncated cone is desired, the `top_radius` parameter may be set to `0`.

   Note that the above dimensions should be interpreted as if the Cone is unrotated. In other
   words, any shape rotation takes place *after* the Cone dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric cone object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, material_density_kg_m3)
      setattr(self.geometry, 'bottom_radius', Symbol(self.name + '_bottom_radius'))
      setattr(self.geometry, 'top_radius', Symbol(self.name + '_top_radius'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Cone`."""
      bottom_radius_mm = 1000.0 * params['bottom_radius']
      top_radius_mm = 1000.0 * params['top_radius']
      height_mm = 1000.0 * params['height']
      return Part.makeCone(bottom_radius_mm, top_radius_mm, height_mm)


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, bottom_radius_m: Union[float, None],
                             top_radius_m: Union[float, None],
                             height_m: Union[float, None]) -> Cone:
      """Sets the physical geometry of the current `Cone` object.

      See the `Cone` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(bottom_radius=bottom_radius_m,
                        top_radius=top_radius_m,
                        height=height_m)
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
      return (math.pi * self.geometry.height / 3.0) * \
             (self.geometry.bottom_radius**2 + self.geometry.top_radius**2 +
              self.geometry.bottom_radius * self.geometry.top_radius)

   @property
   def surface_area(self) -> float:
      return (math.pi * (self.geometry.bottom_radius**2 + self.geometry.top_radius**2)) + \
             (math.pi * (self.geometry.bottom_radius + self.geometry.top_radius) *
              sqrt(self.geometry.height**2 +
                         (self.geometry.bottom_radius - self.geometry.top_radius)**2))

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      rotation_center = self.static_center_of_placement \
                             if self.static_center_of_placement is not None else \
                        Coordinate('rotation_center', x=0.0, y=0.0, z=0.0)
      unoriented_centroid = (self.geometry.bottom_radius - rotation_center.x,
                             0.0 - rotation_center.y,
                             ((self.geometry.height * (self.geometry.bottom_radius**2
                                + (2.0 * self.geometry.bottom_radius * self.geometry.top_radius)
                                + (3.0 * self.geometry.top_radius**2))) /
                              (4.0 * (self.geometry.bottom_radius**2
                                + (self.geometry.bottom_radius * self.geometry.top_radius)
                                + self.geometry.top_radius**2))) - rotation_center.z)
      return self.orientation.rotate_point(rotation_center.as_tuple(), unoriented_centroid)

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.center_of_gravity

   @property
   def unoriented_length(self) -> float:
      return 2.0 * self.geometry.bottom_radius

   @property
   def unoriented_width(self) -> float:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> float:
      return self.geometry.height
