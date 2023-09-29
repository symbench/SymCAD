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
from sympy import Expr, Symbol, Min, Max, sqrt
from . import GenericShape
import math

class EllipticCylinder(GenericShape):
   """Model representing a generic parameteric elliptic cylinder.

   By default, the cylinder is oriented such that its flat faces are perpendicular to the z-axis,
   and its major axis is aligned with the x-axis:

   ![EllipticCylinder](https://symbench.github.io/SymCAD/images/EllipticCylinder.png)

   The `geometry` of this shape includes the following parameters:

   - `major_radius`: Major radius (in `m`) of the EllipticCylinder along the x-axis
   - `minor_radius`: Minor radius (in `m`) of the EllipticCylinder along the y-axis
   - `height`: Height (in `m`) of the EllipticCylinder along the z-axis

   Note that the above dimensions should be interpreted as if the EllipticCylinder is unrotated.
   In other words, any shape rotation takes place *after* the EllipticCylinder dimensions have
   been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric elliptic cylinder object.

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
      """Scripted CAD generation method for an `EllipticCylinder`."""
      doc = FreeCAD.newDocument('Temp')
      height_mm = 1000.0 * params['height']
      major_radius_mm = 1000.0 * params['major_radius']
      minor_radius_mm = 1000.0 * params['minor_radius']
      ellipse1d = doc.addObject('Part::Ellipse', 'Ellipse')
      ellipse1d.MajorRadius = major_radius_mm
      ellipse1d.MinorRadius = minor_radius_mm
      doc.recompute()
      ellipse2d = doc.addObject('Part::Face', 'EllipseFace')
      ellipse2d.Sources = [ellipse1d]
      doc.recompute()
      ellipse = ellipse2d.Shape.extrude(FreeCAD.Vector(0, 0, height_mm))
      FreeCAD.closeDocument(doc.Name)
      return ellipse


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, major_radius_m: Union[float, None],
                             minor_radius_m: Union[float, None],
                             height_m: Union[float, None]) -> EllipticCylinder:
      """Sets the physical geometry of the current `EllipticCylinder` object.

      See the `EllipticCylinder` class documentation for a description of each geometric parameter.
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
      return math.pi * self.geometry.major_radius * \
             self.geometry.minor_radius * self.geometry.height

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (2.0 * math.pi * self.geometry.major_radius * self.geometry.minor_radius) + \
         (self.geometry.height *
            (math.pi * ((3.0 * (self.geometry.major_radius + self.geometry.minor_radius)) -
                        sqrt(((3.0 * self.geometry.major_radius) + self.geometry.minor_radius) *
                             ((3.0 * self.geometry.minor_radius) + self.geometry.major_radius)))))

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return self.geometry.major_radius, self.geometry.minor_radius, 0.5 * self.geometry.height

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.major_radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.minor_radius

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height

   @property
   def oriented_length(self) -> Union[float, Expr]:
      min_x, max_x = 1000000000000.0, -1000000000000.0
      R = self.orientation.get_rotation_matrix_row(0)
      for i in range(0, 360, 20):
        deg_radians = math.radians(i)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), 0.0)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), self.geometry.height)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
      return max_x - min_x

   @property
   def oriented_width(self) -> Union[float, Expr]:
      min_x, max_x = 1000000000000.0, -1000000000000.0
      R = self.orientation.get_rotation_matrix_row(1)
      for i in range(0, 360, 20):
        deg_radians = math.radians(i)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), 0.0)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), self.geometry.height)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
      return max_x - min_x

   @property
   def oriented_height(self) -> Union[float, Expr]:
      min_x, max_x = 1000000000000.0, -1000000000000.0
      R = self.orientation.get_rotation_matrix_row(2)
      for i in range(0, 360, 20):
        deg_radians = math.radians(i)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), 0.0)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
        point = (self.geometry.major_radius * math.cos(deg_radians), self.geometry.minor_radius * math.sin(deg_radians), self.geometry.height)
        x = sum([R[i] * point[i] for i in range(3)])
        min_x = Min(min_x, x)
        max_x = Max(max_x, x)
      return max_x - min_x
