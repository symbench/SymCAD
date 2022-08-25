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
from . import GenericShape
import math

class Capsule(GenericShape):
   """Model representing a generic parameteric capsule.

   By default, the capsule is oriented such that the endcaps are aligned with the z-axis:

   ![Capsule](https://symbench.github.io/SymCAD/images/Capsule.png)

   The `geometry` of this shape includes the following parameters:

   - `cylinder_radius`: Outer radius (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_length`: Length (in `m`) of the center cylindrical part of the Capsule
   - `endcap_length`: Length (in `m`) of a single endcap as measured from its tip to the
                      central cylinder
   - `thickness`: Thickness (in `m`) of the shell of the Capsule
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric capsule object.

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
      setattr(self.geometry, 'endcap_length', Symbol(self.name + '_endcap_length'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Capsule`."""
      doc = FreeCAD.newDocument('Temp')
      thickness_mm = 1000.0 * params['thickness']
      cylinder_length_mm = 1000.0 * params['cylinder_length']
      outer_cylinder_radius_mm = 1000.0 * params['cylinder_radius']
      outer_endcap_length_mm = 1000.0 * params['endcap_length']
      inner_cylinder_radius_mm = outer_cylinder_radius_mm - thickness_mm
      inner_endcap_length_mm = outer_endcap_length_mm - thickness_mm
      if fully_displace:
         cylinder = Part.makeCylinder(outer_cylinder_radius_mm, cylinder_length_mm)
         endcaps = []
         for i in range(2):
            endcap = doc.addObject('Part::Ellipsoid', 'Endcap' + str(i))
            endcap.Radius1 = outer_endcap_length_mm
            endcap.Radius2 = endcap.Radius3 = outer_cylinder_radius_mm
            endcap.Angle1 = 0.0
            endcap.Placement = \
               FreeCAD.Placement(FreeCAD.Vector(0, 0, cylinder_length_mm if i == 0 else 0),
                                 FreeCAD.Rotation(0, 0, 0 if i == 0 else 180))
            endcaps.append(endcap)
         doc.recompute()
         capsule = Part.Solid(cylinder.fuse([endcap.Shape for endcap in endcaps]))
      else:
         cylinder2d = Part.makeRuledSurface(Part.makeCircle(outer_cylinder_radius_mm),
                                            Part.makeCircle(inner_cylinder_radius_mm))
         cylinder = cylinder2d.extrude(FreeCAD.Vector(0, 0, cylinder_length_mm))
         endcaps = []
         for i in range(4):
            endcap = doc.addObject('Part::Ellipsoid', 'Endcap' + str(i))
            endcap.Radius1 = outer_endcap_length_mm if i < 2 else \
                             inner_endcap_length_mm
            endcap.Radius2 = endcap.Radius3 = outer_cylinder_radius_mm if i < 2 else \
                             inner_cylinder_radius_mm
            endcap.Angle1 = 0.0
            endcap.Placement = \
               FreeCAD.Placement(FreeCAD.Vector(0, 0, cylinder_length_mm if i % 2 == 0 else 0),
                                 FreeCAD.Rotation(0, 0, 0 if i % 2 == 0 else 180))
            endcaps.append(endcap)
         doc.recompute()
         capsule = Part.Solid(cylinder.fuse([endcaps[0].Shape.cut(endcaps[2].Shape),
                                             endcaps[1].Shape.cut(endcaps[3].Shape)]))
      FreeCAD.closeDocument(doc.Name)
      return capsule


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, cylinder_radius_m: Union[float, None],
                             cylinder_length_m: Union[float, None],
                             endcap_length_m: Union[float, None],
                             thickness_m: Union[float, None]) -> Capsule:
      """Sets the physical geometry of the current `Capsule` object.

      See the `Capsule` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(cylinder_radius=cylinder_radius_m,
                        cylinder_length=cylinder_length_m,
                        endcap_length=endcap_length_m,
                        thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'cylinder_radius': (0.0, 2.0),
         'cylinder_length': (0.0, 2.0),
         'endcap_length': (0.0, 2.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= (math.pi * (self.geometry.cylinder_radius - self.geometry.thickness)**2
                         * self.geometry.cylinder_length) \
             + ((4.0 * math.pi / 3.0) * (self.geometry.endcap_length - self.geometry.thickness)
                                    * (self.geometry.cylinder_radius - self.geometry.thickness)**2)
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return (math.pi * self.geometry.cylinder_radius**2 * self.geometry.cylinder_length) \
             + ((4.0 * math.pi / 3.0) * self.geometry.endcap_length
                                      * self.geometry.cylinder_radius**2)

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (2.0 * math.pi * self.geometry.cylinder_radius * self.geometry.cylinder_length) \
             + (4.0 * math.pi
                    * (((2.0 * (self.geometry.endcap_length * self.geometry.cylinder_radius)**1.6)
                        + self.geometry.cylinder_radius**3.2) / 3.0)**(1.0/1.6))

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (self.geometry.cylinder_radius,
              self.geometry.cylinder_radius,
              self.geometry.endcap_length + (0.5 * self.geometry.cylinder_length))

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.cylinder_radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.cylinder_length + (2.0 * self.geometry.endcap_length)
