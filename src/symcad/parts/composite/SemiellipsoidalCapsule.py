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

class SemiellipsoidalCapsule(CompositeShape):
   """Model representing a parameteric capsule with semiellipsoidal endcaps.

   By default, the capsule is oriented such that the endcaps are aligned with the x-axis:

   ![SemiellipsoidalCapsule](https://symbench.github.io/SymCAD/images/SemiellipsoidalCapsule.png)

   The minor axis of each endcap spans the open face of the endcap to its tip, while the major
   axis spans the radius of the open face of the endcap itself.

   The `geometry` of this shape includes the following parameters:

   - `cylinder_radius`: Outer radius (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_length`: Length (in `m`) of the center cylindrical part of the Capsule
   - `cylinder_thickness`: Thickness (in `m`) of the cylindrical shell of the Capsule
   - `endcap_radius`: Radius (in `m`) of the semiellipsoidal endcaps of the Capsule
   - `endcap_thickness`: Thickness (in `m`) of the semiellipsoidal endcaps of the Capsule

   Note that the above dimensions should be interpreted as if the capsule is unrotated. In other
   words, any shape rotation takes place *after* the capsule dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str,
                      material_density_kg_m3: Optional[float] = 1.0,
                      major_minor_axis_ratio: Optional[float] = 2.0) -> None:
      """Initializes a parametric capsule object with semiellipsoidal endcaps.

      The `major_minor_axis_ratio` parameter is used to determine the relative axis lengths of a
      semiellipsoidal endcap when one or more of its geometric parameters are symbolic. If all
      parameters are concretely defined, then this parameter is meaningless.

      The minor axis of this shape spans the open face of the endcap to its tip, while the major
      axis spans the radius of the open face of the endcap itself.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      major_minor_axis_ratio : `float`, optional, default=2.0
         Desired major-to-minor axis ratio of the semiellipsoid.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'cylinder_radius', Symbol(self.name + '_cylinder_radius'))
      setattr(self.geometry, 'cylinder_length', Symbol(self.name + '_cylinder_length'))
      setattr(self.geometry, 'cylinder_thickness', Symbol(self.name + '_cylinder_thickness'))
      setattr(self.geometry, 'endcap_radius', Symbol(self.name + '_endcap_radius'))
      setattr(self.geometry, 'endcap_thickness', Symbol(self.name + '_endcap_thickness'))
      self.set_geometry(cylinder_radius_m=None,
                        cylinder_length_m=None,
                        cylinder_thickness_m=None,
                        endcap_radius_m=None,
                        endcap_thickness_m=None,
                        major_minor_axis_ratio=major_minor_axis_ratio)


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for `SemiellipsoidalCapsule`."""
      doc = FreeCAD.newDocument('Temp')
      cylinder_length_mm = 1000.0 * params['cylinder_length']
      outer_cylinder_radius_mm = 1000.0 * params['cylinder_radius']
      inner_cylinder_radius_mm = 1000.0 * (params['cylinder_radius'] - params['cylinder_thickness'])
      outer_endcap_radius_mm = 1000.0 * params['endcap_radius']
      inner_endcap_radius_mm = 1000.0 * (params['endcap_radius'] - params['endcap_thickness'])
      outer_front = doc.addObject('Part::Ellipsoid', 'FrontOuter')
      outer_front.Radius1 = int(outer_endcap_radius_mm)
      outer_front.Radius2 = int(outer_cylinder_radius_mm)
      outer_front.Radius3 = int(outer_cylinder_radius_mm)
      outer_front.Angle1 = 0.0
      outer_back = doc.addObject('Part::Ellipsoid', 'BackOuter')
      outer_back.Radius1 = int(outer_endcap_radius_mm)
      outer_back.Radius2 = int(outer_cylinder_radius_mm)
      outer_back.Radius3 = int(outer_cylinder_radius_mm)
      outer_back.Angle1 = 0.0
      if not fully_displace:
         inner_front = doc.addObject('Part::Ellipsoid', 'FrontInner')
         inner_front.Radius1 = int(inner_endcap_radius_mm)
         inner_front.Radius2 = int(inner_cylinder_radius_mm)
         inner_front.Radius3 = int(inner_cylinder_radius_mm)
         inner_front.Angle1 = 0.0
         inner_back = doc.addObject('Part::Ellipsoid', 'BackInner')
         inner_back.Radius1 = int(inner_endcap_radius_mm)
         inner_back.Radius2 = int(inner_cylinder_radius_mm)
         inner_back.Radius3 = int(inner_cylinder_radius_mm)
         inner_back.Angle1 = 0.0
         doc.recompute()
         front = outer_front.Shape.cut(inner_front.Shape)
         back = outer_back.Shape.cut(inner_back.Shape)
         front.Placement = \
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                              FreeCAD.Rotation(0, -90, 0))
         back.Placement = \
            FreeCAD.Placement(FreeCAD.Vector(cylinder_length_mm, 0, 0),
                              FreeCAD.Rotation(0, 90, 0))
         pipe2d = Part.makeRuledSurface(Part.makeCircle(outer_cylinder_radius_mm),
                                        Part.makeCircle(inner_cylinder_radius_mm))
         pipe = pipe2d.extrude(FreeCAD.Vector(0, 0, cylinder_length_mm))
      else:
         doc.recompute()
         outer_front.Placement = \
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                              FreeCAD.Rotation(0, -90, 0))
         outer_back.Placement = \
            FreeCAD.Placement(FreeCAD.Vector(cylinder_length_mm, 0, 0),
                              FreeCAD.Rotation(0, 90, 0))
         front = outer_front.Shape
         back = outer_back.Shape
         pipe = Part.makeCylinder(outer_cylinder_radius_mm, cylinder_length_mm)
      pipe.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                                         FreeCAD.Rotation(0, 90, 0))
      FreeCAD.closeDocument(doc.Name)
      return pipe.generalFuse([front, back])[0]


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, cylinder_radius_m: Union[float, None],
                             cylinder_length_m: Union[float, None],
                             cylinder_thickness_m: Union[float, None],
                             endcap_radius_m: Union[float, None],
                             endcap_thickness_m: Union[float, None],
                             major_minor_axis_ratio: float = 2.0) -> SemiellipsoidalCapsule:
      """Sets the physical geometry of the current `SemiellipsoidalCapsule` object.

      The `major_minor_axis_ratio` parameter is used to determine the relative axis lengths of a
      semiellipsoidal endcap when one or more of its geometric parameters are symbolic. If all
      parameters are concretely defined, then this parameter is meaningless.

      See the `SemiellipsoidalCapsule` class documentation for a description of each geometric
      parameter.
      """
      self.geometry.set(cylinder_radius=cylinder_radius_m,
                        cylinder_length=cylinder_length_m,
                        cylinder_thickness=cylinder_thickness_m,
                        endcap_radius=endcap_radius_m,
                        endcap_thickness=endcap_thickness_m)
      if cylinder_radius_m is not None and endcap_radius_m is None:
         self.geometry.endcap_radius = cylinder_radius_m / major_minor_axis_ratio
      elif cylinder_radius_m is None and endcap_radius_m is not None:
         self.geometry.cylinder_radius = endcap_radius_m * major_minor_axis_ratio
      elif cylinder_radius_m is None and endcap_radius_m is None:
         self.geometry.endcap_radius = self.geometry.cylinder_radius / major_minor_axis_ratio
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'cylinder_radius': (0.01, 2.0),
         'cylinder_length': (0.01, 2.0),
         'cylinder_thickness': (0.001, 0.05),
         'endcap_radius': (0.01, 1.0),
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
      volume -= ((4.0 * math.pi / 3.0) *
                 (self.geometry.cylinder_radius - self.geometry.cylinder_thickness)**2 *
                 (self.geometry.endcap_radius - self.geometry.endcap_thickness))
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      endcap_volume = (4.0 * math.pi / 3.0) * \
                      self.geometry.cylinder_radius**2 * self.geometry.endcap_radius
      return (math.pi * self.geometry.cylinder_radius**2 * self.geometry.cylinder_length) + \
             endcap_volume

   @property
   def surface_area(self) -> Union[float, Expr]:
      endcap_surface_area = 4.0 * math.pi * \
         ((((self.geometry.endcap_radius * self.geometry.cylinder_radius)**1.6 +
            (self.geometry.endcap_radius * self.geometry.cylinder_radius)**1.6 +
            (self.geometry.cylinder_radius * self.geometry.cylinder_radius)**1.6) / 3.0)**(1.0/1.6))
      return (2.0 * math.pi * self.geometry.cylinder_radius * self.geometry.cylinder_length) + \
             endcap_surface_area

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
      return (2.0 * self.geometry.endcap_radius) + self.geometry.cylinder_length

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
