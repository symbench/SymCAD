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
from typing import Optional, Tuple, Union
from . import EndcapShape
import math, sympy

class Torisphere(EndcapShape):

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      super().__init__(identifier, 'Torisphere.FCStd', material_density_kg_m3)
      setattr(self.geometry, 'base_radius', sympy.Symbol(self.name + '_base_radius'))
      setattr(self.geometry, 'crown_ratio', sympy.Symbol(self.name + '_crown_ratio'))
      setattr(self.geometry, 'knuckle_ratio', sympy.Symbol(self.name + '_knuckle_ratio'))
      setattr(self.geometry, 'thickness', sympy.Symbol(self.name + '_thickness'))


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, base_radius_m: Union[float, None],
                             thickness_m: Union[float, None],
                             crown_ratio_percent: Union[float, None] = 1.0,
                             knuckle_ratio_percent: Union[float, None] = 0.06) -> Torisphere:
      if crown_ratio_percent is not None and crown_ratio_percent > 1.0:
         raise ValueError('crown_ratio_percent ({}) is not a percentage between 0.0 - 1.0'
                          .format(crown_ratio_percent))
      if knuckle_ratio_percent is not None and (knuckle_ratio_percent < 0.06 or
                                                knuckle_ratio_percent > 1.0):
         raise ValueError('knuckle_ratio_percent ({}) is not a percentage between 0.06 - 1.0'
                          .format(knuckle_ratio_percent))
      self.geometry.set(base_radius=base_radius_m,
                        crown_ratio=crown_ratio_percent,
                        knuckle_ratio=knuckle_ratio_percent,
                        thickness=thickness_m)
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def mass(self) -> float:
      return self.material_volume * self.material_density

   @property
   def material_volume(self) -> float:
      knuckle_radius = self.geometry.knuckle_ratio * self.geometry.base_radius
      crown_radius = self.geometry.crown_ratio * self.geometry.crown_ratio
      c = self.geometry.base_radius - knuckle_radius
      h = crown_radius - \
          sympy.sqrt((knuckle_radius + c - crown_radius) *
                     (knuckle_radius - c - crown_radius))
      return (math.pi / 3.0) * ((2.0 * h * crown_radius**2) - \
             (((2.0 * knuckle_radius**2) + c**2 + (2.0 * knuckle_radius * crown_radius)) * (crown_radius - h)) + \
             (3.0 * knuckle_radius**2 * c * sympy.asin((crown_radius - h) / (crown_radius - knuckle_radius))))

   @property
   def displaced_volume(self) -> float:
      return self.material_volume

   @property
   def surface_area(self) -> float:
      return 0#??

   @property
   def centroid(self) -> Tuple[float, float, float]:
      return 0.0, 0.0, self.geometry.base_radius

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      return self.centroid

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.centroid

   @property
   def length(self) -> float:
      knuckle_radius = self.geometry.knuckle_ratio * self.geometry.base_radius
      crown_radius = self.geometry.crown_ratio * self.geometry.crown_ratio
      c = self.geometry.base_radius - knuckle_radius
      return crown_radius - sympy.sqrt((knuckle_radius + c - crown_radius) *
                                       (knuckle_radius - c - crown_radius))

   @property
   def width(self) -> float:
      return 2.0 * self.geometry.base_radius

   @property
   def height(self) -> float:
      return 2.0 * self.geometry.base_radius
