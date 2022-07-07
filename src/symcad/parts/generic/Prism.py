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
from sympy import Expr, Symbol, pi, sin, tan
from . import GenericShape
import math

class Prism(GenericShape):
   """Model representing a generic parameteric prism.

   By default, the prism is oriented such that its height is aligned with the z-axis:

   ![Prism](https://symbench.github.io/SymCAD/images/Prism.png)

   The `geometry` of this shape includes the following parameters:

   - `num_edges`: Number of sides on the Prism
   - `edge_length`: Length (in `m`) of a single side of the Prism
   - `height`: Height (in `m`) of the Prism along the z-axis

   Note that the above dimensions should be interpreted as if the Prism is unrotated. In other
   words, any shape rotation takes place *after* the Prism dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric prism object.

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
      """Scripted CAD generation method for a `Prism`."""
      num_edges = int(params['num_edges'])
      edge_length_mm = 1000.0 * params['edge_length']
      height_mm = 1000.0 * params['height']
      edge_angle = math.radians(360.0 / num_edges)
      vertices = [FreeCAD.Vector(0.5 * edge_length_mm, 0, 0)]
      for i in range(1, num_edges):
         vertices.append(
            FreeCAD.Vector((edge_length_mm * math.cos(i * edge_angle)) + vertices[i-1][0],
                           (edge_length_mm * math.sin(i * edge_angle)) + vertices[i-1][1],
                           0.0))
      vertices.append(FreeCAD.Vector(0.5 * edge_length_mm, 0, 0))
      offset_y = 0.5 * -(max(vertex[1] for vertex in vertices) +
                         min(vertex[1] for vertex in vertices))
      for vertex in vertices:
         vertex[1] += offset_y
      polygon = Part.Face(Part.makePolygon(vertices))
      prism = polygon.extrude(FreeCAD.Vector(0, 0, height_mm))
      return prism


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, num_edges: int,
                             edge_length_m: Union[float, None],
                             height_m: Union[float, None]) -> Prism:
      """Sets the physical geometry of the current `Prism` object.

      See the `Prism` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(num_edges=num_edges, edge_length=edge_length_m, height=height_m)
      return self


   # Built-in function overrides ------------------------------------------------------------------

   def __imul__(self, value: float) -> Prism:
      num_edges = self.geometry.num_edges
      super().__imul__(value)
      self.geometry.num_edges = num_edges
      return self

   def __itruediv__(self, value: float) -> Prism:
      num_edges = self.geometry.num_edges
      super().__itruediv__(value)
      self.geometry.num_edges = num_edges
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      area = 0.5 * self.geometry.num_edges * self.geometry.edge_length * apothem_length
      return area * self.geometry.height

   @property
   def surface_area(self) -> Union[float, Expr]:
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      base_area = self.geometry.num_edges * self.geometry.edge_length * apothem_length
      side_area = self.geometry.num_edges * self.geometry.edge_length * self.geometry.height
      return base_area + side_area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      return  (self.geometry.edge_length / (2.0 * sin(pi / self.geometry.num_edges)),
               apothem_length,
               0.5 * self.geometry.height)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.edge_length \
             / (2.0 * sin(pi / self.geometry.num_edges))

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      apothem_length = self.geometry.edge_length / (2.0 * tan(pi / self.geometry.num_edges))
      return 2.0 * apothem_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height
