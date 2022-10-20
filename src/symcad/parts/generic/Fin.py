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
from sympy import Expr, Symbol, sqrt
from . import GenericShape

class Fin(GenericShape):
   """Model representing a generic parameteric parallelepiped-shaped fin.

   By default, the fin is oriented such that its length follows the x-axis, its width
   follows the y-axis, and its height follows the z-axis:

   ![Fin](https://symbench.github.io/SymCAD/images/Fin.png)

   The `geometry` of this shape includes the following parameters:

   - `lower_length`: Length (in `m`) of the lower edge of the fin along the x-axis
   - `upper_length`: Length (in `m`) of the upper edge of the fin along the x-axis
   - `thickness`: Width (in `m`) of the fin along the y-axis
   - `height`: Distance (in `m`) between the top and bottom edges of the fin

   Note that the above dimensions should be interpreted as if the fin is unrotated.
   In other words, any shape rotation takes place *after* the fin dimensions have
   been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric parallelepiped-shaped fin.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, 'Fin.FCStd', None, material_density_kg_m3)
      setattr(self.geometry, 'lower_length', Symbol(self.name + '_lower_length'))
      setattr(self.geometry, 'upper_length', Symbol(self.name + '_upper_length'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *,
                    lower_length_m: Union[float, None],
                    upper_length_m: Union[float, None],
                    thickness_m: Union[float, None],
                    height_m: Union[float, None]) -> Fin:
      """Sets the physical geometry of the current `Fin` object.

      See the `Fin` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(lower_length=lower_length_m,
                        upper_length=upper_length_m,
                        thickness=thickness_m,
                        height=height_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'lower_length': (0.0, 1.0),
         'upper_length': (0.0, 1.0),
         'thickness': (0.0, 0.5),
         'height': (0.0, 1.5)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      area = (self.geometry.upper_length * self.geometry.height) + \
         (0.5 * (self.geometry.lower_length - self.geometry.upper_length -
                 (0.5 * self.geometry.thickness) - 0.001) * self.geometry.height)
      return area * self.geometry.thickness

   @property
   def surface_area(self) -> Union[float, Expr]:
      area = (self.geometry.upper_length * self.geometry.height) + \
         (0.5 * (self.geometry.lower_length - self.geometry.upper_length) * self.geometry.height)
      return (2.0 * area) + (self.geometry.thickness * self.geometry.height) + \
         (sqrt((self.geometry.lower_length - self.geometry.upper_length)**2 +
               self.geometry.height**2) * self.geometry.thickness)

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      triangle_base_length = self.geometry.lower_length - self.geometry.upper_length
      triangle_mass = 0.5 * (triangle_base_length - (0.5 * self.geometry.thickness) - 0.001) * \
                      self.geometry.height * self.geometry.thickness
      rectangle_mass = self.geometry.upper_length * self.geometry.height * self.geometry.thickness
      total_mass = triangle_mass + rectangle_mass
      triangle_cg_x = 2.0 * triangle_base_length / 3.0
      triangle_cg_z = self.geometry.height / 3.0
      rectangle_cg_x = 0.5 * self.geometry.upper_length
      rectangle_cg_z = 0.5 * self.geometry.height
      return (((triangle_cg_x * triangle_mass) +
               ((triangle_base_length + rectangle_cg_x) * rectangle_mass)) / total_mass,
              0.5 * self.geometry.thickness,
              ((triangle_cg_z * triangle_mass) +
               (rectangle_cg_z * rectangle_mass)) / total_mass)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.lower_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.geometry.thickness

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height
