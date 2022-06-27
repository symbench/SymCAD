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
from ...core.Coordinate import Coordinate
from . import GenericShape
from sympy import Symbol, pi, sqrt, sin, tan, cot
import math

class Pyramid(GenericShape):
   """Model representing a generic parameteric pyramid.

   By default, the pyramid is oriented such that its height is aligned with the z-axis:

   ![Pyramid](https://symbench.github.io/SymCAD/images/Pyramid.png)

   The `geometry` of this shape includes the following parameters:

   - `num_edges`: Number of sides on the Pyramid
   - `edge_length`: Length (in `m`) of a single edge of the base of the Pyramid
   - `height`: Height (in `m`) of the Pyramid along the z-axis

   Note that the above dimensions should be interpreted as if the Pyramid is unrotated. In other
   words, any shape rotation takes place *after* the Pyramid dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric pyramid object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, material_density_kg_m3)
      setattr(self.geometry, 'num_edges', Symbol(self.name + '_num_edges'))
      setattr(self.geometry, 'edge_length', Symbol(self.name + '_edge_length'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Pyramid`."""
      num_edges = int(params['num_edges'])
      edge_length_mm = 1000.0 * params['edge_length']
      height_mm = 1000.0 * params['height']
      edge_angle = math.radians(360.0 / num_edges)
      base_vertices = [FreeCAD.Vector(0.5 * edge_length_mm, 0, 0)]
      tip_vertices = [FreeCAD.Vector(0.5 * 0.000001, 0, height_mm)]
      for i in range(1, num_edges):
         base_vertices.append(
            FreeCAD.Vector((edge_length_mm * math.cos(i * edge_angle)) + base_vertices[i-1][0],
                           (edge_length_mm * math.sin(i * edge_angle)) + base_vertices[i-1][1],
                           0.0))
         tip_vertices.append(
            FreeCAD.Vector((0.000001 * math.cos(i * edge_angle)) + tip_vertices[i-1][0],
                           (0.000001 * math.sin(i * edge_angle)) + tip_vertices[i-1][1],
                           height_mm))
      base_vertices.append(FreeCAD.Vector(0.5 * edge_length_mm, 0, 0))
      tip_vertices.append(FreeCAD.Vector(0.5 * 0.000001, 0, height_mm))
      base_offset_y = 0.5 * -(max(vertex[1] for vertex in base_vertices) +
                              min(vertex[1] for vertex in base_vertices))
      tip_offset_y = 0.5 * -(max(vertex[1] for vertex in tip_vertices) +
                             min(vertex[1] for vertex in tip_vertices))
      for vertex in base_vertices:
         vertex[1] += base_offset_y
      for vertex in tip_vertices:
         vertex[1] += tip_offset_y
      polygon = Part.Face(Part.makePolygon(base_vertices))
      tip = Part.Face(Part.makePolygon(tip_vertices))
      pyramid = Part.makeLoft([polygon.OuterWire, tip.OuterWire], True)
      return pyramid


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, num_edges: int,
                             edge_length_m: Union[float, None],
                             height_m: Union[float, None]) -> Pyramid:
      """Sets the physical geometry of the current `Pyramid` object.

      See the `Pyramid` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(num_edges=num_edges, edge_length=edge_length_m, height=height_m)
      return self


   # Built-in function overrides ------------------------------------------------------------------

   def __imul__(self, value: float) -> Pyramid:
      num_edges = self.geometry.num_edges
      super().__imul__(value)
      self.geometry.num_edges = num_edges
      return self

   def __itruediv__(self, value: float) -> Pyramid:
      num_edges = self.geometry.num_edges
      super().__itruediv__(value)
      self.geometry.num_edges = num_edges
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
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      base_area = 0.5 * self.geometry.num_edges * self.geometry.edge_length * apothem_length
      return self.geometry.height * base_area / 3.0

   @property
   def surface_area(self) -> float:
      base_perimeter = self.geometry.num_edges * self.geometry.edge_length
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      slant_height = sqrt(self.geometry.height**2 +
                                (0.25 * self.geometry.edge_length**2 *
                                 cot(pi / self.geometry.num_edges)**2))
      base_area = 0.5 * self.geometry.num_edges * self.geometry.edge_length * apothem_length
      side_area = 0.5 * base_perimeter * slant_height
      return base_area + side_area

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      rotation_center = self.static_center_of_placement \
                             if self.static_center_of_placement is not None else \
                        Coordinate('rotation_center', x=0.0, y=0.0, z=0.0)
      unoriented_centroid = ((self.geometry.edge_length /
                                 (2.0 * sin(pi / self.geometry.num_edges)))
                               - rotation_center.x,
                             0.0 - rotation_center.y,
                             (0.25 * self.geometry.height) - rotation_center.z)
      return self.orientation.rotate_point(rotation_center.as_tuple(), unoriented_centroid)

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.center_of_gravity

   @property
   def unoriented_length(self) -> float:
      return 2.0 * self.geometry.edge_length \
             / (2.0 * sin(pi / self.geometry.num_edges))

   @property
   def unoriented_width(self) -> float:
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      return 2.0 * apothem_length

   @property
   def unoriented_height(self) -> float:
      return self.geometry.height