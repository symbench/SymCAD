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

class CamberedAirfoil(GenericShape):
   """Model representing a generic parameteric cambered airfoil.

   By default, the airfoil is oriented such that its length follows the x-axis, its span follows
   the y-axis, and its thickness follows the z-axis:

   ![CamberedAirfoil](https://symbench.github.io/SymCAD/images/CamberedAirfoil.png)

   The `geometry` of this shape includes the following parameters:

   - `max_camber`: Maximum camber (in `%`) of the airfoil
   - `max_camber_location`: Location of the maximum camber (in `% of length`) of the airfoil
      along the x-axis
   - `max_thickness`: Maximum thickenss (in `% of length`) of the airfoil along the z-axis
   - `chord_length`: Length (in `m`) of the x-axis chord of the airfoil
   - `span`: Width (in `m`) of the y-axis of the airfoil

   Note that the above dimensions should be interpreted as if the airfoil is unrotated. In other
   words, any shape rotation takes place *after* the airfoil dimensions have been specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: Optional[float] = 1.0) -> None:
      """Initializes a generic parametric cambered airfoil object.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'max_camber', Symbol(self.name + '_max_camber'))
      setattr(self.geometry, 'max_camber_location', Symbol(self.name + '_max_camber_location'))
      setattr(self.geometry, 'max_thickness', Symbol(self.name + '_max_thickness'))
      setattr(self.geometry, 'chord_length', Symbol(self.name + '_chord_length'))
      setattr(self.geometry, 'span', Symbol(self.name + '_span'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `CamberedAirfoil`."""
      doc = FreeCAD.newDocument('Temp')
      max_camber_percent = params['max_camber']
      max_camber_location_percent = params['max_camber_location']
      max_thickness_percent = params['max_thickness']
      chord_length_mm = 1000.0 * params['chord_length']
      span_mm = 1000.0 * params['span']
      def z_val(x: float) -> float:
         return 5.0 * max_thickness_percent * chord_length_mm * (
            (0.2969 * x**0.5) - (0.1260 * x) - (0.3516 * x**2) + (0.2843 * x**3) - (0.1036 * x**4))
      sketch_object = None
      x, points = 0.0, [FreeCAD.Vector(0, 0)]
      while x <= 1.0:
         points.append(FreeCAD.Vector(x, z_val(x)))
         x += 0.01
      sketch_object.addGeometry(Part.BSplineCurve(points, None, None, False, 3, None, False), False)
      FreeCAD.closeDocument(doc.Name)
      return None


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, length_m: Union[float, None],
                             width_m: Union[float, None],
                             height_m: Union[float, None],
                             thickness_m: Union[float, None]) -> Box:
      """Sets the physical geometry of the current `Box` object.

      See the `Box` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(length=length_m, width=width_m, height=height_m, thickness=thickness_m)
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'length': (0.0, 2.0),
         'width': (0.0, 2.0),
         'height': (0.0, 2.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= ((self.geometry.length - 2.0*self.geometry.thickness) *
                 (self.geometry.width - 2.0*self.geometry.thickness) *
                 (self.geometry.height - 2.0*self.geometry.thickness))
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return self.geometry.length * self.geometry.width * self.geometry.height

   @property
   def surface_area(self) -> Union[float, Expr]:
      return (2.0 * self.geometry.length * self.geometry.width) + \
             (2.0 * self.geometry.length * self.geometry.height) + \
             (2.0 * self.geometry.width * self.geometry.height)

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (0.5 * self.geometry.length,
              0.5 * self.geometry.width,
              0.5 * self.geometry.height)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.geometry.width

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.height
