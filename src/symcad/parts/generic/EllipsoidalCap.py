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
from sympy import Expr, Symbol, sqrt
from . import GenericShape
import math

class EllipsoidalCap(GenericShape):
   """Model representing a generic parameteric ellipsoidal cap.

   By default, the cap is oriented such that its flat face is perpendicular to the z-axis,
   and its rounded edge points upward:

   ![EllipsoidalCap](https://symbench.github.io/SymCAD/images/EllipsoidalCap.png)

   The `geometry` of this shape includes the following parameters:

   - `major_radius`: Major radius (in `m`) of the EllipsoidalCap along the x- and y-axis
   - `minor_radius`: Minor radius (in `m`) of the EllipsoidalCap along the z-axis
   - `height`: Height (in `m`) of the EllipsoidalCap along the z-axis (determines where the
               ellipsoid will be cut along its minor radius)

   Note that the above dimensions should be interpreted as if the EllipsoidalCap is unrotated.
   In other words, any shape rotation takes place *after* the EllipsoidalCapr dimensions have
   been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric ellipsoidal cap object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'major_radius', Symbol(self.name + '_major_radius'))
      setattr(self.geometry, 'minor_radius', Symbol(self.name + '_minor_radius'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for an `EllipsoidalCap`."""
      doc = FreeCAD.newDocument('Temp')
      height_mm = 1000.0 * params['height']
      major_radius_mm = 1000.0 * params['major_radius']
      minor_radius_mm = 1000.0 * params['minor_radius']
      ellipsoid = doc.addObject('Part::Ellipsoid', 'Ellipsoid')
      ellipsoid.Radius1 = minor_radius_mm
      ellipsoid.Radius2 = major_radius_mm
      ellipsoid.Radius3 = major_radius_mm
      ellipsoid.Angle1 = math.degrees(math.asin((minor_radius_mm - height_mm) / minor_radius_mm))
      doc.recompute()
      cap = ellipsoid.Shape
      FreeCAD.closeDocument(doc.Name)
      return cap


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, major_radius_m: Union[float, None],
                             minor_radius_m: Union[float, None],
                             height_m: Union[float, None]) -> EllipsoidalCap:
      """Sets the physical geometry of the current `EllipsoidalCap` object.

      See the `EllipsoidalCap` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(major_radius=major_radius_m,
                        minor_radius=minor_radius_m,
                        height=height_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'major_radius': (0.0, 2.0),
         'minor_radius': (0.0, 2.0),
         'height': (0.0, 2.0)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return (math.pi * self.geometry.major_radius**2 * self.geometry.height**2 *
                ((3.0 * self.geometry.minor_radius) - self.geometry.height)) / \
             (3.0 * self.geometry.minor_radius**2)

   @property
   def surface_area(self) -> Union[float, Expr]:
      base_area = (math.pi * self.geometry.major_radius**2 * self.geometry.height *
                     ((2.0 * self.geometry.minor_radius) - self.geometry.height)) /\
                  self.geometry.minor_radius**2
      base_radius_squared = base_area / math.pi
      return (math.pi * (base_radius_squared + self.geometry.height**2)) + base_area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      base_area = (math.pi * self.geometry.major_radius**2 * self.geometry.height *
                     ((2.0 * self.geometry.minor_radius) - self.geometry.height)) /\
                  self.geometry.minor_radius**2
      base_radius = sqrt(base_area / math.pi)
      z_centroid = ((3.0 * ((2.0 * self.geometry.minor_radius) - self.geometry.height)**2) /
                    (4.0 * ((3.0 * self.geometry.minor_radius) - self.geometry.height))) - \
                   (self.geometry.minor_radius - self.geometry.height)
      return base_radius, base_radius, z_centroid

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      base_area = (math.pi * self.geometry.major_radius**2 * self.geometry.height *
                     ((2.0 * self.geometry.minor_radius) - self.geometry.height)) /\
                  self.geometry.minor_radius**2
      return 2.0 * sqrt(base_area / math.pi)

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height
