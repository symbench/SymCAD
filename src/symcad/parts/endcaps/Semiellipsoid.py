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
from . import EndcapShape
import math

class Semiellipsoid(EndcapShape):
   """Model representing a hollow, parametric, semiellipsoidal endcap.

   By default, the endcap is oriented such that its base is perpendicular to the z-axis:

   ![Semiellipsoid](https://symbench.github.io/SymCAD/images/Semiellipsoid.png)

   The minor axis of this shape spans the open face of the endcap to its tip, while the major
   axis spans the radius of the open face itself.

   The `geometry` of this shape includes the following parameters:

   - `major_radius`: Major radius (in `m`) of the Semiellipsoid along the x- and y-axis
   - `minor_radius`: Minor radius (in `m`) of the Semiellipsoid along the z-axis
   - `thickness`: Thickness (in `m`) of the shell of the Semiellipsoid

   Note that the above dimensions should be interpreted as if the Semiellipsoid is unrotated.
   In other words, any shape rotation takes place *after* the Semiellipsoid dimensions have been
   specified.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str,
                      material_density_kg_m3: Optional[float] = 1.0,
                      major_minor_axis_ratio: Optional[float] = 2.0,
                      minor_depends_on_major: bool = True) -> None:
      """Initializes a hollow, parametric, ellipsoidal endcap object.

      The `major_minor_axis_ratio` and `minor_depends_on_major` parameters are used to determine
      the relative axis lengths of the Semiellipsoid when one or more of its geometric parameters
      are symbolic. If all parameters are concretely defined, then these parameters are
      meaningless.

      The minor axis of this shape spans the open face of the endcap to its tip, while the major
      axis spans the radius of the open face itself.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      major_minor_axis_ratio : `float`, optional, default=2.0
         Desired major-to-minor axis ratio of the semiellipsoid.
      minor_depends_on_major : `bool`, optional, default=True
         Whether the radius of the minor axis depends on the major axis or vice versa.
      """
      super().__init__(identifier,
                       self.__create_cad__,
                       'Semiellipsoid.tar.xz',
                       material_density_kg_m3)
      setattr(self.geometry, 'major_radius', Symbol(self.name + '_major_radius'))
      setattr(self.geometry, 'minor_radius', Symbol(self.name + '_minor_radius'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))
      self.set_geometry(major_axis_radius_m=None,
                        minor_axis_radius_m=None,
                        thickness_m=None,
                        major_minor_axis_ratio=major_minor_axis_ratio,
                        minor_depends_on_major=minor_depends_on_major)


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      """Scripted CAD generation method for a `Semiellipsoid`."""
      doc = FreeCAD.newDocument('Temp')
      thickness_mm = 1000.0 * params['thickness']
      outer_major_radius_mm = 1000.0 * params['major_radius']
      outer_minor_radius_mm = 1000.0 * params['minor_radius']
      inner_major_radius_mm = outer_major_radius_mm - thickness_mm
      inner_minor_radius_mm = outer_minor_radius_mm - thickness_mm
      outer = doc.addObject('Part::Ellipsoid', 'Ellipsoid')
      outer.Radius1 = outer_minor_radius_mm
      outer.Radius2 = outer_major_radius_mm
      outer.Radius3 = outer_major_radius_mm
      outer.Angle1 = 0.0
      if not fully_displace:
         inner = doc.addObject('Part::Ellipsoid', 'Ellipsoid')
         inner.Radius1 = inner_minor_radius_mm
         inner.Radius2 = inner_major_radius_mm
         inner.Radius3 = inner_major_radius_mm
         inner.Angle1 = 0.0
         doc.recompute()
         endcap = outer.Shape.cut(inner.Shape)
      else:
         doc.recompute()
         endcap = outer.Shape
      FreeCAD.closeDocument(doc.Name)
      return endcap


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, major_axis_radius_m: Union[float, None],
                             minor_axis_radius_m: Union[float, None],
                             thickness_m: Union[float, None],
                             major_minor_axis_ratio: float = 2.0,
                             minor_depends_on_major: bool = True) -> Semiellipsoid:
      """Sets the physical geometry of the current `Semiellipsoid` object.

      The `major_minor_axis_ratio` and `minor_depends_on_major` parameters are used to determine
      the relative axis lengths of the Semiellipsoid when one or more of its geometric parameters
      are symbolic. If all parameters are concretely defined, then these parameters are
      meaningless.

      See the `Semiellipsoid` class documentation for a description of each geometric parameter.
      """
      self.geometry.set(major_radius=major_axis_radius_m,
                        minor_radius=minor_axis_radius_m,
                        thickness=thickness_m)
      if major_axis_radius_m is not None and minor_axis_radius_m is None:
         self.geometry.minor_radius = major_axis_radius_m / major_minor_axis_ratio
      elif major_axis_radius_m is None and minor_axis_radius_m is not None:
         self.geometry.major_radius = minor_axis_radius_m * major_minor_axis_ratio
      elif major_axis_radius_m is None and minor_axis_radius_m is None:
         if minor_depends_on_major:
            self.geometry.minor_radius = self.geometry.major_radius / major_minor_axis_ratio
         else:
            self.geometry.major_radius = self.geometry.minor_radius * major_minor_axis_ratio
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      parameter_bounds = {
         'major_radius': (0.0, 2.0),
         'minor_radius': (0.0, 2.0),
         'thickness': (0.0, 0.05)
      }
      return parameter_bounds.get(parameter, (0.0, 0.0))


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      volume = self.displaced_volume
      volume -= (2.0 * math.pi * (self.geometry.major_radius - self.geometry.thickness)**2
                               * (self.geometry.minor_radius - self.geometry.thickness) / 3.0)
      return volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return 2.0 * math.pi * self.geometry.major_radius**2 * self.geometry.minor_radius / 3.0

   @property
   def surface_area(self) -> Union[float, Expr]:
      numerator = (2.0 * (self.geometry.minor_radius * self.geometry.major_radius)**1.6) + \
                  self.geometry.major_radius**3.2
      return 2.0 * math.pi * (numerator / 3.0)**(1.0 / 1.6)

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (self.geometry.major_radius,
              self.geometry.major_radius,
              self.__neural_net__.evaluate('cg_z', **self.geometry.as_dict()))

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return (self.geometry.major_radius,
              self.geometry.major_radius,
              3.0 * self.geometry.minor_radius / 8.0)

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return 2.0 * self.geometry.major_radius

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.unoriented_length

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.geometry.minor_radius
