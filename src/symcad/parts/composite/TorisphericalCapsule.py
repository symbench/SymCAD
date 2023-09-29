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
from sympy import Expr, Symbol, sqrt, cos, asin
from . import CompositeShape
import math

class TorisphericalCapsule(CompositeShape):
   """Model representing a parameteric capsule with torispherical endcaps.

   By default, the capsule is oriented such that the endcaps are aligned with the x-axis:

   ![TorisphericalCapsule](https://symbench.github.io/SymCAD/images/TorisphericalCapsule.png)

   The `geometry` of this shape includes the following parameters:

   - `cylinder_radius`: Outer radius (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_length`: Length (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_thickness`: Thickness (in `m`) of the cylindrical shell of the Capsule
   - `endcap_thickness`: Thickness (in `m`) of the torispherical endcaps of the Capsule
   - `crown_ratio`: Ratio (in `%`) of the radius of the crown of the torispherical
                    endcap to the `cylinder_radius`
   - `knuckle_ratio`: Ratio (in `%`) of the radius of the knuckle of the torispherical
                      endcap to the `cylinder_radius`

   Note that the above dimensions should be interpreted as if the capsule is unrotated. In other
   words, any shape rotation takes place *after* the capsule dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a parametric capsule object with torispherical endcaps.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, 'TorisphericalCapsule.FCStd', None, material_density_kg_m3)
      setattr(self.geometry, 'cylinder_radius', Symbol(self.name + '_cylinder_radius'))
      setattr(self.geometry, 'cylinder_length', Symbol(self.name + '_cylinder_length'))
      setattr(self.geometry, 'cylinder_thickness', Symbol(self.name + '_cylinder_thickness'))
      setattr(self.geometry, 'endcap_thickness', Symbol(self.name + '_endcap_thickness'))
      setattr(self.geometry, 'crown_ratio', Symbol(self.name + '_crown_ratio'))
      setattr(self.geometry, 'knuckle_ratio', Symbol(self.name + '_knuckle_ratio'))


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, cylinder_radius_m: Union[float, None],
                             cylinder_length_m: Union[float, None],
                             cylinder_thickness_m: Union[float, None],
                             endcap_thickness_m: Union[float, None],
                             crown_ratio_percent: Union[float, None] = 1.0,
                             knuckle_ratio_percent: Union[float, None] = 0.06) -> TorisphericalCapsule:
      """Sets the physical geometry of the current `TorisphericalCapsule` object.

      See the `TorisphericalCapsule` class documentation for a description of each geometric
      parameter.
      """
      if crown_ratio_percent is not None and crown_ratio_percent > 1.0:
         raise ValueError('crown_ratio_percent ({}) is not a percentage between 0.0 - 1.0'
                          .format(crown_ratio_percent))
      if knuckle_ratio_percent is not None and (knuckle_ratio_percent < 0.06 or
                                                knuckle_ratio_percent > 1.0):
         raise ValueError('knuckle_ratio_percent ({}) is not a percentage between 0.06 - 1.0'
                          .format(knuckle_ratio_percent))
      self.geometry.set(cylinder_radius=cylinder_radius_m,
                        cylinder_length=cylinder_length_m,
                        cylinder_thickness=cylinder_thickness_m,
                        endcap_thickness=endcap_thickness_m,
                        crown_ratio=crown_ratio_percent,
                        knuckle_ratio=knuckle_ratio_percent)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'cylinder_radius': (0.01, 2.0),
         'cylinder_length': (0.01, 2.0),
         'cylinder_thickness': (0.001, 0.05),
         'endcap_thickness': (0.001, 0.05),
         'crown_ratio': (0.0, 1.0),
         'knuckle_ratio': (0.06, 1.0)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      knuckle_radius = (2.0 * self.geometry.knuckle_ratio * self.geometry.cylinder_radius) - \
                       self.geometry.endcap_thickness
      crown_radius = (2.0 * self.geometry.crown_ratio * self.geometry.cylinder_radius) - \
                     self.geometry.endcap_thickness
      c = self.geometry.cylinder_radius - self.geometry.endcap_thickness - knuckle_radius
      h = crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                              (knuckle_radius - c - crown_radius))
      volume = self.displaced_volume
      volume -= ((math.pi / 3.0) * \
                 ((2.0 * h * crown_radius**2) -
                  (((2.0 * knuckle_radius**2) + c**2 +
                    (2.0 * knuckle_radius * crown_radius)) * (crown_radius - h)) +
                  (3.0 * knuckle_radius**2 * c *
                         asin((crown_radius - h) / (crown_radius - knuckle_radius)))))
      volume -= (math.pi
                 * (self.geometry.cylinder_radius - self.geometry.cylinder_thickness)**2
                 * self.geometry.cylinder_length)
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.cylinder_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.cylinder_radius
      c = self.geometry.cylinder_radius - knuckle_radius
      h = crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                              (knuckle_radius - c - crown_radius))
      endcap_volume = (math.pi / 3.0) * \
                      ((2.0 * h * crown_radius**2) -
                       (((2.0 * knuckle_radius**2) + c**2 +
                         (2.0 * knuckle_radius * crown_radius)) * (crown_radius - h)) +
                       (3.0 * knuckle_radius**2 * c *
                              asin((crown_radius - h) / (crown_radius - knuckle_radius))))
      return (math.pi * self.geometry.cylinder_radius**2 * self.geometry.cylinder_length) + \
             (2.0 * endcap_volume)

   @property
   def surface_area(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.cylinder_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.cylinder_radius
      cos_alpha = cos(asin((1.0 - (2.0 * self.geometry.knuckle_ratio)) /
                           (2.0 * (self.geometry.crown_ratio - self.geometry.knuckle_ratio))))
      a2 = knuckle_radius * cos_alpha
      endcap_area = (4.0 * math.pi * crown_radius**2 * (1.0 - cos_alpha)) + \
                    (4.0 * math.pi * knuckle_radius *
                       (a2 + ((self.geometry.cylinder_radius - knuckle_radius) * asin(cos_alpha))))
      return (2.0 * math.pi * self.geometry.cylinder_radius * self.geometry.cylinder_length) + \
             endcap_area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (0.5 * self.unoriented_length,
              0.5 * self.unoriented_width,
              0.5 * self.unoriented_height)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      knuckle_radius = 2.0 * self.geometry.knuckle_ratio * self.geometry.cylinder_radius
      crown_radius = 2.0 * self.geometry.crown_ratio * self.geometry.cylinder_radius
      c = self.geometry.cylinder_radius - knuckle_radius
      endcap_length = crown_radius - sqrt((knuckle_radius + c - crown_radius) *
                                          (knuckle_radius - c - crown_radius))
      return (2.0 * endcap_length) + self.geometry.cylinder_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.cylinder_radius

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.unoriented_width

   @property
   def oriented_length(self) -> Union[float, Expr]:
      # TODO: Implement this
      return 0

   @property
   def oriented_width(self) -> Union[float, Expr]:
      # TODO: Implement this
      return 0

   @property
   def oriented_height(self) -> Union[float, Expr]:
      # TODO: Implement this
      return 0
