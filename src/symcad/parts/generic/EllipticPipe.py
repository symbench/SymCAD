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

class EllipticPipe(GenericShape):
   """Model representing a generic parameteric elliptic pipe.

   By default, the pipe is oriented such that its hollow portion is aligned with the z-axis, and
   its major axis is aligned with the x-axis.

   ![EllipticPipe](https://symbench.github.io/SymCAD/images/EllipticPipe.png)

   The `geometry` of this shape includes the following parameters:

   - `major_radius`: Major outer radius (in `m`) of the EllipticPipe along the x-axis
   - `minor_radius`: Minor outer radius (in `m`) of the EllipticPipe along the y-axis
   - `height`: Outer height (in `m`) of the EllipticPipe along the z-axis
   - `thickness`: Thickness (in `m`) of the shell of the EllipticPipe

   Note that the above dimensions should be interpreted as if the EllipticPipe is unrotated. In
   other words, any shape rotation takes place *after* the EllipticPipe dimensions have been
   specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric elliptic pipe object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      placement_point : `Coordinate`, optional, default=`(0, 0, 0)`
         Local point (in percent length) on the unoriented `SymPart` that is used for rotation
         and placement.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'major_radius', Symbol(self.name + '_major_radius'))
      setattr(self.geometry, 'minor_radius', Symbol(self.name + '_minor_radius'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for an `EllipticPipe`."""
      doc = FreeCAD.newDocument('Temp')
      ellipse_part_type = 'Part::Ellipse'
      height_mm = 1000.0 * params['height']
      thickness_mm = 1000.0 * params['thickness']
      outer_major_radius_mm = 1000.0 * params['major_radius']
      outer_minor_radius_mm = 1000.0 * params['minor_radius']
      inner_major_radius_mm = outer_major_radius_mm - thickness_mm
      inner_minor_radius_mm = outer_minor_radius_mm - thickness_mm
      if fully_displace:
         ellipse1d = doc.addObject(ellipse_part_type, 'Ellipse')
         ellipse1d.MajorRadius = outer_major_radius_mm
         ellipse1d.MinorRadius = outer_minor_radius_mm
         doc.recompute()
         ellipse2d = doc.addObject('Part::Face', 'EllipseFace')
         ellipse2d.Sources = [ellipse1d]
         doc.recompute()
         ellipse = ellipse2d.Shape.extrude(FreeCAD.Vector(0, 0, height_mm))
      else:
         outer_ellipse2d = doc.addObject(ellipse_part_type, 'Outer')
         outer_ellipse2d.MajorRadius = outer_major_radius_mm
         outer_ellipse2d.MinorRadius = outer_minor_radius_mm
         inner_ellipse2d = doc.addObject(ellipse_part_type, 'Inner')
         inner_ellipse2d.MajorRadius = inner_major_radius_mm
         inner_ellipse2d.MinorRadius = inner_minor_radius_mm
         doc.recompute()
         ellipse2d = Part.makeRuledSurface(outer_ellipse2d.Shape, inner_ellipse2d.Shape)
         ellipse = ellipse2d.extrude(FreeCAD.Vector(0, 0, height_mm))
      FreeCAD.closeDocument(doc.Name)
      return ellipse


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, major_radius_m: Union[float, None],
                             minor_radius_m: Union[float, None],
                             height_m: Union[float, None],
                             thickness_m: Union[float, None]) -> EllipticPipe:
      """Sets the physical geometry of the current `EllipticPipe` object.

      See the `EllipticPipe` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(major_radius=major_radius_m,
                        minor_radius=minor_radius_m,
                        height=height_m,
                        thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'major_radius': (0.0, 2.0),
         'minor_radius': (0.0, 2.0),
         'height': (0.0, 2.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= (math.pi * (self.geometry.major_radius - self.geometry.thickness) * \
             (self.geometry.minor_radius - self.geometry.thickness) * self.geometry.height)
      return volume

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
