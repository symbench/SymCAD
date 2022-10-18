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

class SymmetricAirfoil(GenericShape):
   """Model representing a generic parameteric symmetric airfoil.

   By default, the airfoil is oriented such that its length follows the x-axis, its span follows
   the y-axis, and its thickness follows the z-axis:

   ![SymmetricAirfoil](https://symbench.github.io/SymCAD/images/SymmetricAirfoil.png)

   The `geometry` of this shape includes the following parameters:

   - `max_thickness`: Maximum thickness (in `% of length`) of the airfoil along the z-axis
   - `chord_length`: Length (in `m`) of the x-axis chord of the airfoil
   - `span`: Width (in `m`) of the y-axis of the airfoil
   - `material_thickness`: Thickness (in `m`) of the structural material of the airfoil

   Note that the above dimensions should be interpreted as if the airfoil is unrotated. In other
   words, any shape rotation takes place *after* the airfoil dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric symmetric airfoil object.

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
      setattr(self.geometry, 'material_thickness', Symbol(self.name + '_material_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def z_val(x: float, max_thickness: float, chord_length: float) -> float:
      return 5.0 * max_thickness * chord_length * (
         (0.2969 * x**0.5) - (0.1260 * x) - (0.3516 * x**2) + (0.2843 * x**3) - (0.1036 * x**4))

   @staticmethod
   def __create_cad__(params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `SymmetricAirfoil`."""
      doc = FreeCAD.newDocument('Temp')
      material_thickness_mm = 1000.0 * params['material_thickness']
      max_thickness_percent = params['max_thickness']
      outer_chord_length_mm = 1000.0 * params['chord_length']
      inner_chord_length_mm = outer_chord_length_mm - (2.0 * material_thickness_mm)
      inner_max_thickness_percent = ((max_thickness_percent * outer_chord_length_mm) -
                                     material_thickness_mm) / inner_chord_length_mm
      outer_span_mm = 1000.0 * params['span']
      inner_span_mm = outer_span_mm - (2.0 * material_thickness_mm)
      x, points_upper_outer, points_lower_outer = 0.0, [], []
      points_upper_inner, points_lower_inner = [], []
      while x <= 1.009:
         points_upper_outer.append(FreeCAD.Vector(x * outer_chord_length_mm,
                                   SymmetricAirfoil.z_val(x, max_thickness_percent,
                                                             outer_chord_length_mm)))
         points_lower_outer.append(FreeCAD.Vector(x * outer_chord_length_mm,
                                   -SymmetricAirfoil.z_val(x, max_thickness_percent,
                                                              outer_chord_length_mm)))
         points_upper_inner.append(FreeCAD.Vector(material_thickness_mm +
                                                  x * inner_chord_length_mm,
                                   SymmetricAirfoil.z_val(x, inner_max_thickness_percent,
                                                             inner_chord_length_mm)))
         points_lower_inner.append(FreeCAD.Vector(material_thickness_mm +
                                                  x * inner_chord_length_mm,
                                   -SymmetricAirfoil.z_val(x, inner_max_thickness_percent,
                                                              inner_chord_length_mm)))
         x += 0.01
      outer_body = doc.addObject('PartDesign::Body','Outer')
      outer_sketch = doc.addObject('Sketcher::SketchObject', 'OuterSketch')
      outer_sketch.Support = doc.XZ_Plane
      outer_sketch.MapMode = 'FlatFace'
      outer_body.addObject(outer_sketch)
      outer_sketch.addGeometry(Part.BSplineCurve(points_upper_outer, None, None,
                                                 False, 3, None, False), False)
      outer_sketch.addGeometry(Part.BSplineCurve(points_lower_outer, None, None,
                                                 False, 3, None, False), False)
      outer_pad = doc.addObject('PartDesign::Pad', 'OuterPad')
      outer_body.addObject(outer_pad)
      outer_pad.Length = outer_span_mm
      outer_pad.Profile = outer_sketch
      inner_body = doc.addObject('PartDesign::Body','Inner')
      inner_sketch = doc.addObject('Sketcher::SketchObject', 'InnerSketch')
      inner_sketch.Support = doc.XZ_Plane
      inner_sketch.MapMode = 'FlatFace'
      inner_body.addObject(inner_sketch)
      inner_sketch.addGeometry(Part.BSplineCurve(points_upper_inner, None, None,
                                                 False, 3, None, False), False)
      inner_sketch.addGeometry(Part.BSplineCurve(points_lower_inner, None, None,
                                                 False, 3, None, False), False)
      inner_pad = doc.addObject('PartDesign::Pad', 'InnerPad')
      inner_body.addObject(inner_pad)
      inner_pad.Length = inner_span_mm
      inner_pad.Profile = inner_sketch
      inner_body.Placement = FreeCAD.Placement(FreeCAD.Vector(0, -material_thickness_mm, 0),
                                               FreeCAD.Rotation(0, 0, 0))
      doc.recompute()
      airfoil = outer_body.Shape.cut(inner_body.Shape)
      FreeCAD.closeDocument(doc.Name)
      return airfoil


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, max_thickness_percent: Union[float, None],
                             chord_length_m: Union[float, None],
                             span_m: Union[float, None],
                             material_thickness_m: Union[float, None]) -> SymmetricAirfoil:
      """Sets the physical geometry of the current `SymmetricAirfoil` object.

      See the `SymmetricAirfoil` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(max_thickness=max_thickness_percent,
                        chord_length=chord_length_m,
                        span=span_m,
                        material_thickness=material_thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'max_thickness': (0.01, 0.90),
         'chord_length': (0.1, 2.0),
         'span': (0.0, 2.0),
         'material_thickness': (0.005, 0.02)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      inner_chord_length = self.geometry.chord_length - (2.0 * self.geometry.material_thickness)
      inner_max_thickness_percent = \
         ((self.geometry.material_thickness * self.geometry.chord_length) -
          self.geometry.material_thickness) / inner_chord_length
      x, points_upper_outer, points_upper_inner = 0.0, [], []
      while x <= 1.009:
         points_upper_outer.append((x * self.geometry.chord_length,
                                    SymmetricAirfoil.z_val(x, self.geometry.max_thickness,
                                                             self.geometry.chord_length)))
         points_upper_inner.append((self.geometry.material_thickness + (x * inner_chord_length),
                                    SymmetricAirfoil.z_val(x, inner_max_thickness_percent,
                                                             inner_chord_length)))
         x += 0.01
      area = 0.0
      for i in range(1, len(points_upper_outer) - 1):
         area += points_upper_outer[i][1]
      area = points_upper_outer[0][1] + (2.0 * area) + points_upper_outer[len(points_upper_outer)-1][1]
      h = (points_upper_outer[len(points_upper_outer)-1][0] - points_upper_outer[0][0]) / (len(points_upper_outer) - 1)
      volume_outer = 0.5 * h * area * self.geometry.span
      area = 0.0
      for i in range(1, len(points_upper_inner) - 1):
         area += points_upper_inner[i][1]
      area = points_upper_inner[0][1] + (2.0 * area) + points_upper_inner[len(points_upper_inner)-1][1]
      h = (points_upper_inner[len(points_upper_inner)-1][0] - points_upper_inner[0][0]) / (len(points_upper_inner) - 1)
      volume_inner = 0.5 * h * area * (self.geometry.span - (2.0 * self.geometry.material_thickness))
      return volume_outer - volume_inner

   @property
   def surface_area(self) -> Union[float, Expr]:
      x, points_upper = 0.0, []
      while x <= 1.009:
         points_upper.append((x * self.geometry.chord_length,
                              SymmetricAirfoil.z_val(x, self.geometry.max_thickness,
                                                        self.geometry.chord_length)))
         x += 0.01
      area = 0.0
      for i in range(1, len(points_upper)):
         x_diff = (points_upper[i][0] - points_upper[i-1][0])
         y_diff = (points_upper[i][1] - points_upper[i-1][1])
         area += sqrt(x_diff**2 + y_diff**2)
      area = (2.0 * area) * self.geometry.span
      return area

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (0.41 * self.geometry.chord_length,
              0.5 * self.geometry.span,
              0.5 * self.geometry.max_thickness * self.geometry.chord_length)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.chord_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.geometry.span

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.max_thickness * self.geometry.chord_length
