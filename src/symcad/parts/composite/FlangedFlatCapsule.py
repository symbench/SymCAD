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
from sympy import Expr, Symbol
from . import CompositeShape
import math

class FlangedFlatCapsule(CompositeShape):
   """Model representing a parameteric capsule with flanged flat endcaps.

   By default, the capsule is oriented such that the endcaps are aligned with the x-axis:

   ![FlangedFlatCapsule](https://symbench.github.io/SymCAD/images/FlangedFlatCapsule.png)

   The `geometry` of this shape includes the following parameters:

   - `cylinder_radius`: Outer radius (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_length`: Length (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_thickness`: Thickness (in `m`) of the cylindrical shell of the Capsule
   - `endcap_thickness`: Thickness (in `m`) of the flat endcaps of the Capsule

   Note that the above dimensions should be interpreted as if the capsule is unrotated. In other
   words, any shape rotation takes place *after* the capsule dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a parametric capsule object with flanged flat endcaps.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'cylinder_radius', Symbol(self.name + '_cylinder_radius'))
      setattr(self.geometry, 'cylinder_length', Symbol(self.name + '_cylinder_length'))
      setattr(self.geometry, 'cylinder_thickness', Symbol(self.name + '_cylinder_thickness'))
      setattr(self.geometry, 'endcap_thickness', Symbol(self.name + '_endcap_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for `FlangedFlatCapsule`."""
      cylinder_length_mm = 1000.0 * params['cylinder_length']
      outer_cylinder_radius_mm = 1000.0 * params['cylinder_radius']
      inner_cylinder_radius_mm = 1000.0 * (params['cylinder_radius'] - params['cylinder_thickness'])
      endcap_thickness_mm = 1000.0 * params['endcap_thickness']
      front = Part.makeCylinder(outer_cylinder_radius_mm, endcap_thickness_mm)
      front = front.makeFillet(endcap_thickness_mm - 0.001, front.Edges[0:1])
      rear = Part.makeCylinder(outer_cylinder_radius_mm, endcap_thickness_mm)
      rear = rear.makeFillet(endcap_thickness_mm - 0.001, rear.Edges[0:1])
      if fully_displace:
         pipe = Part.makeCylinder(outer_cylinder_radius_mm, cylinder_length_mm)
      else:
         pipe2d = Part.makeRuledSurface(Part.makeCircle(outer_cylinder_radius_mm),
                                        Part.makeCircle(inner_cylinder_radius_mm))
         pipe = pipe2d.extrude(FreeCAD.Vector(0, 0, cylinder_length_mm))
      pipe.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                                         FreeCAD.Rotation(0, 90, 0))
      front.Placement = \
         FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                           FreeCAD.Rotation(0, -90, 0))
      rear.Placement = \
         FreeCAD.Placement(FreeCAD.Vector(cylinder_length_mm, 0, 0),
                           FreeCAD.Rotation(0, 90, 0))
      return front.generalFuse([pipe, rear])[0]


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, cylinder_radius_m: Union[float, None],
                             cylinder_length_m: Union[float, None],
                             cylinder_thickness_m: Union[float, None],
                             endcap_thickness_m: Union[float, None]) -> FlangedFlatCapsule:
      """Sets the physical geometry of the current `FlangedFlatCapsule` object.

      See the `FlangedFlatCapsule` class documentation for a description of each geometric
      parameter.
      """
      self.geometry.set(cylinder_radius=cylinder_radius_m,
                        cylinder_length=cylinder_length_m,
                        cylinder_thickness=cylinder_thickness_m,
                        endcap_thickness=endcap_thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'cylinder_radius': (0.01, 2.0),
         'cylinder_length': (0.01, 2.0),
         'cylinder_thickness': (0.001, 0.05),
         'endcap_thickness': (0.001, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= (math.pi
                 * (self.geometry.cylinder_radius - self.geometry.cylinder_thickness)**2
                 * self.geometry.cylinder_length)
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return (math.pi * self.geometry.cylinder_radius**2 * self.geometry.cylinder_length) + \
             (2.0 * math.pi * self.geometry.endcap_thickness * self.geometry.cylinder_radius**2)

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (2.0 * math.pi * self.geometry.cylinder_radius * self.geometry.cylinder_length) + \
             (2.0 * math.pi * self.geometry.cylinder_radius * self.geometry.endcap_thickness)

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
      return (2.0 * self.geometry.endcap_thickness) + self.geometry.cylinder_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.cylinder_radius

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.unoriented_width
