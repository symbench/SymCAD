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
from sympy import Expr, Symbol, sqrt, sin, cos
from . import CompositeShape
import math

class YFormAirfoils(CompositeShape):
   """Model representing a set of Y-form parameteric airfoils.

   By default, the airfoils are oriented in the following configuration:

   ![YFormAirfoils](https://symbench.github.io/SymCAD/images/YFormAirfoils.png)

   The `geometry` of this shape includes the following parameters:

   - `max_thickness`: Maximum thickness (in `% of length`) of each airfoil
   - `chord_length`: Length (in `m`) of the chord of each airfoil
   - `span`: Width (in `m`) of each airfoil
   - `separation_radius`: Radius (in `m`) of separation between each airfoil
   - `curvature_tilt`: Amount of tilt (in `deg`) of each airfoil

   Note that the above dimensions should be interpreted as if the airfoils are unrotated. In other
   words, any shape rotation takes place *after* the airfoil dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a Y-form parametric airfoil object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'max_thickness', Symbol(self.name + '_max_thickness'))
      setattr(self.geometry, 'chord_length', Symbol(self.name + '_chord_length'))
      setattr(self.geometry, 'span', Symbol(self.name + '_span'))
      setattr(self.geometry, 'separation_radius', Symbol(self.name + '_separation_radius'))
      setattr(self.geometry, 'curvature_tilt', Symbol(self.name + '_curvature_tilt'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def z_val(x: float, max_thickness: float, chord_length: float) -> float:
      return 5.0 * max_thickness * chord_length * (
         (0.2969 * x**0.5) - (0.1260 * x) - (0.3516 * x**2) + (0.2843 * x**3) - (0.1036 * x**4))

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for `YFormAirfoils`."""
      doc = FreeCAD.newDocument('Temp')
      max_thickness_percent = params['max_thickness']
      chord_length_mm = 1000.0 * params['chord_length']
      span_mm = 1000.0 * params['span']
      separation_radius_mm = 1000.0 * params['separation_radius']
      curvature_tilt = params['curvature_tilt']
      x, points_upper, points_lower = 0.0, [], []
      while x <= 1.009:
         points_upper.append(FreeCAD.Vector(x * chord_length_mm,
                                            YFormAirfoils.z_val(x, max_thickness_percent,
                                                                   chord_length_mm)))
         points_lower.append(FreeCAD.Vector(x * chord_length_mm,
                                            -YFormAirfoils.z_val(x, max_thickness_percent,
                                                                    chord_length_mm)))
         x += 0.01
      bodies = []
      for i in range(3):
         body = doc.addObject('PartDesign::Body','Airfoil' + str(i))
         sketch = doc.addObject('Sketcher::SketchObject', 'Sketch' + str(i))
         sketch.Support = doc.XZ_Plane
         sketch.MapMode = 'FlatFace'
         body.addObject(sketch)
         sketch.addGeometry(Part.BSplineCurve(points_upper, None, None,
                                              False, 3, None, False), False)
         sketch.addGeometry(Part.BSplineCurve(points_lower, None, None,
                                              False, 3, None, False), False)
         pad = doc.addObject('PartDesign::Pad', 'Pad' + str(i))
         body.addObject(pad)
         pad.Length = span_mm
         pad.Profile = sketch
         y_offset = sin(math.pi / 3.0) * separation_radius_mm
         z_offset = cos(math.pi / 3.0) * separation_radius_mm
         placement_vector = \
            FreeCAD.Vector(0, y_offset if i == 1 else (-y_offset if i == 2 else 0),
                              -z_offset if i == 1 or i == 2 else separation_radius_mm)
         body.Placement = FreeCAD.Placement(placement_vector,
                          FreeCAD.Rotation(-curvature_tilt if i == 1 else
                                           (curvature_tilt if i == 2 else 0),
                                           curvature_tilt if i == 0 else 0, -90.0 - (i * 120.0)))
         bodies.append(body)
      fusion = doc.addObject('Part::MultiFuse', 'Fusion')
      fusion.Shapes = bodies
      doc.recompute()
      airfoils = fusion.Shape
      FreeCAD.closeDocument(doc.Name)
      return airfoils


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, max_thickness_percent: Union[float, None],
                             chord_length_m: Union[float, None],
                             span_m: Union[float, None],
                             separation_radius_m: Union[float, None],
                             curvature_tilt_deg: Union[float, None]) -> YFormAirfoils:
      """Sets the physical geometry of the current `YFormAirfoils` object.

      See the `YFormAirfoils` class documentation for a description of each geometric
      parameter.
      """
      self.geometry.set(max_thickness=max_thickness_percent,
                        chord_length=chord_length_m,
                        span=span_m,
                        separation_radius=separation_radius_m,
                        curvature_tilt=curvature_tilt_deg)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'max_thickness': (0.01, 0.90),
         'chord_length': (0.1, 2.0),
         'span': (0.0, 2.0),
         'separation_radius': (0.0, 1.5),
         'curvature_tilt': (0.0, 45.0)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      x, points_upper = 0.0, []
      while x <= 1.009:
         points_upper.append((x * self.geometry.chord_length,
                              YFormAirfoils.z_val(x, self.geometry.max_thickness,
                                                     self.geometry.chord_length)))
         x += 0.01
      area = 0.0
      for i in range(1, len(points_upper) - 1):
         area += points_upper[i][1]
      area = points_upper[0][1] + (2.0 * area) + points_upper[len(points_upper)-1][1]
      h = (points_upper[len(points_upper)-1][0] - points_upper[0][0]) / (len(points_upper) - 1)
      return 3.0 * h * area * self.geometry.span

   @property
   def surface_area(self) -> Union[float, Expr]:
      x, points_upper = 0.0, []
      while x <= 1.009:
         points_upper.append((x * self.geometry.chord_length,
                              YFormAirfoils.z_val(x, self.geometry.max_thickness,
                                                     self.geometry.chord_length)))
         x += 0.01
      area = 0.0
      for i in range(1, len(points_upper)):
         x_diff = (points_upper[i][0] - points_upper[i-1][0])
         y_diff = (points_upper[i][1] - points_upper[i-1][1])
         area += sqrt(x_diff**2 + y_diff**2)
      area = (2.0 * area) * self.geometry.span
      return 3.0 * area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      cosine = cos(self.geometry.curvature_tilt * math.pi / 180.0)
      sine = sin(self.geometry.curvature_tilt * math.pi / 180.0)
      return ((0.41 * cosine * self.geometry.chord_length) + (0.5 * sine * self.geometry.span),
              0.5 * self.unoriented_width,
              self.unoriented_height / 3.0)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      cosine = cos(self.geometry.curvature_tilt * math.pi / 180.0)
      sine = sin(self.geometry.curvature_tilt * math.pi / 180.0)
      return (cosine * self.geometry.chord_length) + (sine * self.geometry.span)

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      cosine = cos(self.geometry.curvature_tilt * math.pi / 180.0)
      y_offset = sin(math.pi / 3.0) * self.geometry.separation_radius
      y_width = cos(math.pi / 6.0) * (cosine * self.geometry.span)
      return 2.0 * (y_offset + y_width)

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      cosine = cos(self.geometry.curvature_tilt * math.pi / 180.0)
      z_offset = cos(math.pi / 3.0) * self.geometry.separation_radius
      z_width = sin(math.pi / 6.0) * (cosine * self.geometry.span)
      return z_offset + z_width + self.geometry.separation_radius + self.geometry.span
