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
from typing import List, Optional, Tuple, Union
from sympy import Expr, Symbol, sqrt, asin, cos
from . import EndcapShape
import math

class Torisphere(EndcapShape):
   """Model representing a hollow, parametric, torispherical endcap.

   By default, the endcap is oriented such that its base is perpendicular to the z-axis:

   ![Torisphere](https://symbench.github.io/SymCAD/images/Torisphere.png)

   The `geometry` of this shape includes the following parameters:

   - `base_radius`: Radius (in `m`) of the base of the Torisphere
   - `crown_ratio`: Radius (in `m`) of the tip of the Torisphere
   - `knuckle_ratio`: Height (in `m`) of the Torisphere from base to tip
   - `thickness`: Thickness (in `m`) of the shell of the Torisphere

   ![TorisphereGeometry](https://symbench.github.io/SymCAD/images/TorisphereGeometry.png)

   TODO: Talk about geometry

   Note that the above dimensions should be interpreted as if the Torisphere is unrotated.
   In other words, any shape rotation takes place *after* the Torisphere dimensions have been
   specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a hollow, parametric,torispherical endcap object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, 'Torisphere.FCStd', material_density_kg_m3)
      setattr(self.geometry, 'base_radius', Symbol(self.name + '_base_radius'))
      setattr(self.geometry, 'crown_ratio', Symbol(self.name + '_crown_ratio'))
      setattr(self.geometry, 'knuckle_ratio', Symbol(self.name + '_knuckle_ratio'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # SymPart function overrides ------------------------------------------------------------------

   def __imul__(self, value: float) -> Torisphere:
      crown_ratio = self.geometry.crown_ratio
      knuckle_ratio = self.geometry.knuckle_ratio
      super().__imul__(value)
      self.geometry.crown_ratio = crown_ratio
      self.geometry.knuckle_ratio = knuckle_ratio
      return self

   def __itruediv__(self, value: float) -> Torisphere:
      crown_ratio = self.geometry.crown_ratio
      knuckle_ratio = self.geometry.knuckle_ratio
      super().__itruediv__(value)
      self.geometry.crown_ratio = crown_ratio
      self.geometry.knuckle_ratio = knuckle_ratio
      return self


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, base_radius_m: Union[float, None],
                             thickness_m: Union[float, None],
                             crown_ratio_percent: Union[float, None] = 1.0,
                             knuckle_ratio_percent: Union[float, None] = 0.06) -> Torisphere:
      """Sets the physical geometry of the current `Torisphere` object.

      See the `Torisphere` class documentation for a description of each geometric parameter.
      """
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
   def material_volume(self) -> Union[float, Expr]:
      knuckle_radius = (2.0 * self.geometry.knuckle_ratio * self.geometry.base_radius) - \
                       self.geometry.thickness
      crown_radius = (2.0 * self.geometry.crown_ratio * self.geometry.base_radius) - \
                     self.geometry.thickness
      c = self.geometry.base_radius - self.geometry.thickness - knuckle_radius
      h = crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                              (knuckle_radius - c - crown_radius))
      volume = self.displaced_volume
      volume -= ((math.pi / 3.0) * \
                 ((2.0 * h * crown_radius**2) -
                  (((2.0 * knuckle_radius**2) + c**2 +
                    (2.0 * knuckle_radius * crown_radius)) * (crown_radius - h)) +
                  (3.0 * knuckle_radius**2 * c *
                         asin((crown_radius - h) / (crown_radius - knuckle_radius)))))
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.base_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.base_radius
      c = self.geometry.base_radius - knuckle_radius
      h = crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                              (knuckle_radius - c - crown_radius))
      return (math.pi / 3.0) * \
             ((2.0 * h * crown_radius**2) -
              (((2.0 * knuckle_radius**2) + c**2 +
                (2.0 * knuckle_radius * crown_radius)) * (crown_radius - h)) +
              (3.0 * knuckle_radius**2 * c *
                     asin((crown_radius - h) / (crown_radius - knuckle_radius))))

   @property
   def surface_area(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.base_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.base_radius
      cos_alpha = cos(asin((1.0 - (2.0 * self.geometry.knuckle_ratio)) /
                           (2.0 * (self.geometry.crown_ratio - self.geometry.knuckle_ratio))))
      a2 = knuckle_radius * cos_alpha
      return (4.0 * math.pi * crown_radius**2 * (1.0 - cos_alpha)) + \
             (4.0 * math.pi * knuckle_radius *
                  (a2 + ((self.geometry.base_radius - knuckle_radius) * asin(cos_alpha))))

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (self.geometry.base_radius,
              self.geometry.base_radius,
              0.5 * self.unoriented_height)  # TODO: Fix the z-value

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return (self.geometry.base_radius,
              self.geometry.base_radius,
              0.375 * self.unoriented_height)  # TODO: Fix the z-value

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.base_radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.base_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.base_radius
      c = self.geometry.base_radius - knuckle_radius
      return crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                                 (knuckle_radius - c - crown_radius))
