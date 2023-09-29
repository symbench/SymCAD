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
from sympy import Expr, Symbol, sqrt, atan2, sin, tan
from . import EndcapShape
import math

class ConicalFrustrum(EndcapShape):
   """Model representing a hollow, parametric, conical frustrum.

   By default, the frustrum is oriented such that its base is perpendicular to the z-axis:

   ![ConicalFrustrum](https://symbench.github.io/SymCAD/images/ConicalFrustrum.png)

   The `geometry` of this shape includes the following parameters:

   - `bottom_radius`: Radius (in `m`) of the base of the ConicalFrustrum
                      (must be larger than `top_radius`)
   - `top_radius`: Radius (in `m`) of the tip of the ConicalFrustrum
   - `height`: Height (in `m`) of the ConicalFrustrum from base to tip
   - `thickness`: Thickness (in `m`) of the shell of the ConicalFrustrum

   Note that the above dimensions should be interpreted as if the ConicalFrustrum is unrotated.
   In other words, any shape rotation takes place *after* the ConicalFrustrum dimensions have been
   specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a hollow, parametric, conical frustrum object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'bottom_radius', Symbol(self.name + '_bottom_radius'))
      setattr(self.geometry, 'top_radius', Symbol(self.name + '_top_radius'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `ConicalFrustrum`."""
      height_angle = math.atan2(params['height'], params['bottom_radius'] - params['top_radius'])
      thickness_mm = 1000.0 * params['thickness']
      outer_height_mm = 1000.0 * params['height']
      outer_bottom_radius_mm = 1000.0 * params['bottom_radius']
      outer_top_radius_mm = 1000.0 * params['top_radius']
      inner_height_mm = outer_height_mm - thickness_mm
      inner_bottom_radius_mm = outer_bottom_radius_mm - (thickness_mm / math.sin(height_angle))
      inner_top_radius_mm = inner_bottom_radius_mm - (inner_height_mm / math.tan(height_angle))
      outer = Part.makeCone(outer_bottom_radius_mm, outer_top_radius_mm, outer_height_mm)
      if not fully_displace:
         inner = Part.makeCone(inner_bottom_radius_mm, inner_top_radius_mm, inner_height_mm)
         return outer.cut(inner)
      else:
         return outer


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, bottom_radius_m: Union[float, None],
                             top_radius_m: Union[float, None],
                             height_m: Union[float, None],
                             thickness_m: Union[float, None]) -> ConicalFrustrum:
      """Sets the physical geometry of the current `ConicalFrustrum` object.

      See the `ConicalFrustrum` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(bottom_radius=bottom_radius_m,
                        top_radius=top_radius_m,
                        height=height_m,
                        thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'bottom_radius': (0.0, 2.0),
         'top_radius': (0.0, 2.0),
         'thickness': (0.0, 0.05),
         'height': (0.0, 2.0)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      height_angle = atan2(self.geometry.height,
                           self.geometry.bottom_radius - self.geometry.top_radius)
      inner_height = self.geometry.height - self.geometry.thickness
      inner_bottom_radius = self.geometry.bottom_radius - \
                            (self.geometry.thickness / sin(height_angle))
      inner_top_radius = inner_bottom_radius - (inner_height / tan(height_angle))
      volume -= ((inner_height * math.pi / 3.0) * \
                 (inner_bottom_radius**2 + inner_top_radius**2 +
                    (inner_bottom_radius * inner_top_radius)))
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return (self.geometry.height * math.pi / 3.0) * \
             (self.geometry.bottom_radius**2 + self.geometry.top_radius**2 +
                (self.geometry.bottom_radius * self.geometry.top_radius))

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (math.pi * self.geometry.top_radius**2) + \
             (math.pi * (self.geometry.bottom_radius + self.geometry.top_radius) *
              sqrt(self.geometry.height**2 +
                         (self.geometry.bottom_radius - self.geometry.top_radius)**2))

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (self.geometry.bottom_radius,
              self.geometry.bottom_radius,
              (self.geometry.height *
                 (self.geometry.bottom_radius +
                    (0.5 * self.geometry.top_radius**2) +
                    (2.0 * self.geometry.top_radius))) /
              (3.0 * (self.geometry.bottom_radius + self.geometry.top_radius)))

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return (self.geometry.bottom_radius,
              self.geometry.bottom_radius,
              (self.geometry.height * (self.geometry.bottom_radius**2 +
                 (2.0 * self.geometry.bottom_radius * self.geometry.top_radius) +
                 (3.0 * self.geometry.top_radius**2))) /
              (4.0 * (self.geometry.bottom_radius**2 +
                 (self.geometry.bottom_radius * self.geometry.top_radius) +
                 self.geometry.top_radius**2)))

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.bottom_radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height

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
