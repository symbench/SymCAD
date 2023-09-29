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
from sympy import Expr, Symbol, sqrt, atan2, sin, tan
from . import FairingShape
import math

class CylinderWithConicalEnds(FairingShape):
   """Model representing a cylindrical fairing shape with conical end sections.

   By default, the part is oriented in the following way:

   ![FairingCylinderWithConicalEnds](https://symbench.github.io/SymCAD/images/FairingCylinderWithConicalEnds.png)
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a fairing shape defined by a cylindrical center with conical end sections.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'nose_tip_radius', Symbol(self.name + '_nose_tip_radius'))
      setattr(self.geometry, 'nose_length', Symbol(self.name + '_nose_length'))
      setattr(self.geometry, 'body_radius', Symbol(self.name + '_body_radius'))
      setattr(self.geometry, 'body_length', Symbol(self.name + '_body_length'))
      setattr(self.geometry, 'tail_tip_radius', Symbol(self.name + '_tail_tip_radius'))
      setattr(self.geometry, 'tail_length', Symbol(self.name + '_tail_length'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `CylinderWithConicalEnds`."""
      nose_length_angle = math.atan2(params['nose_length'],
                                     params['body_radius'] - params['nose_tip_radius'])
      tail_length_angle = math.atan2(params['tail_length'],
                                     params['body_radius'] - params['tail_tip_radius'])
      outer_nose_tip_radius_mm = 1000.0 * params['nose_tip_radius']
      outer_nose_length_mm = 1000.0 * params['nose_length']
      outer_body_radius_mm = 1000.0 * params['body_radius']
      body_length_mm = 1000.0 * params['body_length']
      outer_tail_tip_radius_mm = 1000.0 * params['tail_tip_radius']
      outer_tail_length_mm = 1000.0 * params['tail_length']
      thickness_mm = 1000.0 * params['thickness']
      inner_nose_length_mm = outer_nose_length_mm - thickness_mm
      inner_tail_length_mm = outer_tail_length_mm - thickness_mm
      inner_body_radius_mm = outer_body_radius_mm - thickness_mm
      inner_nose_body_radius_mm = outer_body_radius_mm - \
                                  (thickness_mm / math.sin(nose_length_angle))
      inner_tail_body_radius_mm = outer_body_radius_mm - \
                                  (thickness_mm / math.sin(tail_length_angle))
      inner_nose_tip_radius_mm = inner_nose_body_radius_mm - \
                                 (inner_nose_length_mm / math.tan(nose_length_angle))
      inner_tail_tip_radius_mm = inner_tail_body_radius_mm - \
                                 (inner_tail_length_mm / math.tan(tail_length_angle))
      outer_nose = \
         Part.makeCone(outer_body_radius_mm, outer_nose_tip_radius_mm, outer_nose_length_mm)
      outer_tail = \
         Part.makeCone(outer_body_radius_mm, outer_tail_tip_radius_mm, outer_tail_length_mm)
      body2d = Part.makeRuledSurface(Part.makeCircle(outer_body_radius_mm),
                                       Part.makeCircle(inner_body_radius_mm))
      body = body2d.extrude(FreeCAD.Vector(0, 0, body_length_mm))
      inner_nose = \
         Part.makeCone(inner_nose_body_radius_mm, inner_nose_tip_radius_mm, inner_nose_length_mm)
      inner_tail = \
         Part.makeCone(inner_tail_body_radius_mm, inner_tail_tip_radius_mm, inner_tail_length_mm)
      nose = outer_nose.cut(inner_nose)
      tail = outer_tail.cut(inner_tail)
      nose.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(0, 270.0, 0))
      body.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(0, 90.0, 0))
      tail.Placement = FreeCAD.Placement(FreeCAD.Vector(body_length_mm, 0, 0),
                                         FreeCAD.Rotation(0, 90.0, 0))
      return nose.generalFuse([body, tail])[0]


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, nose_tip_radius_m: Union[float, None],
                             nose_length_m: Union[float, None],
                             body_radius_m: Union[float, None],
                             body_length_m: Union[float, None],
                             tail_tip_radius_m: Union[float, None],
                             tail_length_m: Union[float, None],
                             thickness_m: Union[float, None]) -> CylinderWithConicalEnds:
      """Sets the physical geometry of the current `CylinderWithConicalEnds` object.

      See the `CylinderWithConicalEnds` class documentation for a description of each
      geometric parameter.
      """
      self.geometry.set(nose_tip_radius=nose_tip_radius_m,
                        nose_length=nose_length_m,
                        body_radius=body_radius_m,
                        body_length=body_length_m,
                        tail_tip_radius=tail_tip_radius_m,
                        tail_length=tail_length_m,
                        thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'nose_tip_radius': (0.01, 1.5),
         'nose_length': (0.1, 3.0),
         'body_radius': (0.250, 1.5),
         'body_length': (0.015, 3.0),
         'tail_tip_radius': (0.01, 1.5),
         'tail_length': (0.1, 3.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      nose_volume = (math.pi * self.geometry.nose_length / 3.0) * \
             (self.geometry.body_radius**2 + self.geometry.nose_tip_radius**2 +
              self.geometry.body_radius * self.geometry.nose_tip_radius)
      tail_volume = (math.pi * self.geometry.tail_length / 3.0) * \
             (self.geometry.body_radius**2 + self.geometry.tail_tip_radius**2 +
              self.geometry.body_radius * self.geometry.tail_tip_radius)
      body_volume = math.pi * self.geometry.body_radius**2 * self.geometry.body_length
      nose_angle = atan2(self.geometry.nose_length,
                         self.geometry.body_radius - self.geometry.nose_tip_radius)
      nose_inner_height = self.geometry.nose_length - self.geometry.thickness
      nose_inner_body_radius = self.geometry.body_radius - \
                               (self.geometry.thickness / sin(nose_angle))
      nose_inner_tip_radius = nose_inner_body_radius - (nose_inner_height / tan(nose_angle))
      nose_inner_volume = ((nose_inner_height * math.pi / 3.0) * \
                           (nose_inner_body_radius**2 + nose_inner_tip_radius**2 +
                              (nose_inner_body_radius * nose_inner_tip_radius)))
      tail_angle = atan2(self.geometry.tail_length,
                         self.geometry.body_radius - self.geometry.tail_tip_radius)
      tail_inner_height = self.geometry.tail_length - self.geometry.thickness
      tail_inner_body_radius = self.geometry.body_radius - \
                               (self.geometry.thickness / sin(tail_angle))
      tail_inner_tip_radius = tail_inner_body_radius - (tail_inner_height / tan(tail_angle))
      tail_inner_volume = ((tail_inner_height * math.pi / 3.0) * \
                           (tail_inner_body_radius**2 + tail_inner_tip_radius**2 +
                              (tail_inner_body_radius * tail_inner_tip_radius)))
      body_inner_volume = math.pi * (self.geometry.body_radius - self.geometry.thickness)**2 * \
                          self.geometry.body_length
      return nose_volume + tail_volume + body_volume - \
         nose_inner_volume - tail_inner_volume - body_inner_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return self.material_volume

   @property
   def surface_area(self) -> Union[float, Expr]:
      nose_area = (math.pi * self.geometry.nose_tip_radius**2) + \
                  (math.pi * (self.geometry.body_radius + self.geometry.nose_tip_radius) *
                  sqrt(self.geometry.nose_length**2 +
                              (self.geometry.body_radius - self.geometry.nose_tip_radius)**2))
      tail_area = (math.pi * self.geometry.tail_tip_radius**2) + \
                  (math.pi * (self.geometry.body_radius + self.geometry.tail_tip_radius) *
                  sqrt(self.geometry.tail_length**2 +
                              (self.geometry.body_radius - self.geometry.tail_tip_radius)**2))
      body_area = 2.0 * math.pi * self.geometry.body_radius * self.geometry.body_length
      return nose_area + tail_area + body_area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      nose_volume = (math.pi * self.geometry.nose_length / 3.0) * \
             (self.geometry.body_radius**2 + self.geometry.nose_tip_radius**2 +
              self.geometry.body_radius * self.geometry.nose_tip_radius)
      tail_volume = (math.pi * self.geometry.tail_length / 3.0) * \
             (self.geometry.body_radius**2 + self.geometry.tail_tip_radius**2 +
              self.geometry.body_radius * self.geometry.tail_tip_radius)
      body_volume = math.pi * self.geometry.body_radius**2 * self.geometry.body_length
      nose_angle = atan2(self.geometry.nose_length,
                         self.geometry.body_radius - self.geometry.nose_tip_radius)
      nose_inner_height = self.geometry.nose_length - self.geometry.thickness
      nose_inner_body_radius = self.geometry.body_radius - \
                               (self.geometry.thickness / sin(nose_angle))
      nose_inner_tip_radius = nose_inner_body_radius - (nose_inner_height / tan(nose_angle))
      nose_inner_volume = ((nose_inner_height * math.pi / 3.0) * \
                           (nose_inner_body_radius**2 + nose_inner_tip_radius**2 +
                              (nose_inner_body_radius * nose_inner_tip_radius)))
      tail_angle = atan2(self.geometry.tail_length,
                         self.geometry.body_radius - self.geometry.tail_tip_radius)
      tail_inner_height = self.geometry.tail_length - self.geometry.thickness
      tail_inner_body_radius = self.geometry.body_radius - \
                               (self.geometry.thickness / sin(tail_angle))
      tail_inner_tip_radius = tail_inner_body_radius - (tail_inner_height / tan(tail_angle))
      tail_inner_volume = ((tail_inner_height * math.pi / 3.0) * \
                           (tail_inner_body_radius**2 + tail_inner_tip_radius**2 +
                              (tail_inner_body_radius * tail_inner_tip_radius)))
      body_inner_volume = math.pi * (self.geometry.body_radius - self.geometry.thickness)**2 * \
                          self.geometry.body_length
      nose_volume = nose_volume - nose_inner_volume
      body_volume = body_volume - body_inner_volume
      tail_volume = tail_volume - tail_inner_volume
      total_volume = nose_volume + body_volume + tail_volume
      nose_cg_x = self.geometry.nose_length - \
         ((self.geometry.nose_length *
             (self.geometry.body_radius +
                (0.5 * self.geometry.nose_tip_radius**2) +
                (2.0 * self.geometry.nose_tip_radius))) /
          (3.0 * (self.geometry.body_radius + self.geometry.nose_tip_radius)))
      tail_cg_x = self.geometry.nose_length + self.geometry.body_length + \
         ((self.geometry.tail_length *
             (self.geometry.body_radius +
                (0.5 * self.geometry.tail_tip_radius**2) +
                (2.0 * self.geometry.tail_tip_radius))) /
          (3.0 * (self.geometry.body_radius + self.geometry.tail_tip_radius)))
      body_cg_x = self.geometry.nose_length + (0.5 * self.geometry.body_length)
      cg_x = ((nose_cg_x * nose_volume) + (body_cg_x * body_volume) + (tail_cg_x * tail_volume)) \
             / total_volume
      return (cg_x,
              self.geometry.body_radius,
              self.geometry.body_radius)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.nose_length + self.geometry.body_length + self.geometry.tail_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.body_radius

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
