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
from typing import Optional, Tuple, Union
from . import EndcapShape
import sympy

class Semiellipsoid(EndcapShape):

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str,
                      material_density_kg_m3: Optional[float] = 1.0,
                      minor_major_axis_ratio: Optional[float] = 2.0) -> None:
      super().__init__(identifier, 'Semiellipsoid.FCStd', material_density_kg_m3)
      setattr(self.geometry, 'axis_ratio', minor_major_axis_ratio)
      setattr(self.geometry, 'radius_major', sympy.Symbol(self.name + '_radius_major'))
      setattr(self.geometry, 'radius_minor', sympy.Symbol(self.name + '_radius_minor'))
      setattr(self.geometry, 'thickness', sympy.Symbol(self.name + '_thickness'))


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, major_axis_length_m: Union[float, None],
                             minor_axis_radius_m: Union[float, None],
                             thickness_m: Union[float, None],
                             minor_major_axis_ratio: float = 2.0,
                             major_depends_on_minor: bool = True) -> Semiellipsoid:
      self.geometry.set(axis_ratio=minor_major_axis_ratio,
                        radius_major=major_axis_length_m,
                        radius_minor=minor_axis_radius_m,
                        thickness=thickness_m)
      if major_axis_length_m is not None and minor_axis_radius_m is not None:
         self.geometry.axis_ratio = minor_axis_radius_m / major_axis_length_m
      elif major_axis_length_m is not None and minor_axis_radius_m is None:
         self.geometry.radius_minor = self.geometry.radius_major * minor_major_axis_ratio
      elif major_axis_length_m is None and minor_axis_radius_m is not None:
         self.geometry.radius_major = self.geometry.radius_minor / minor_axis_radius_m
      elif major_depends_on_minor:
         self.geometry.radius_major = self.geometry.radius_minor / minor_axis_radius_m
      else:
         self.geometry.radius_minor = self.geometry.radius_major * minor_major_axis_ratio
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def mass(self) -> float:
      return self.material_volume * self.material_density

   @property
   def material_volume(self) -> float:
      pass

   @property
   def displaced_volume(self) -> float:
      pass

   @property
   def surface_area(self) -> float:
      pass

   @property
   def centroid(self) -> Tuple[float, float, float]:
      pass

   @property
   def center_of_gravity(self) -> Tuple[float, float, float]:
      return self.centroid

   @property
   def center_of_buoyancy(self) -> Tuple[float, float, float]:
      return self.centroid

   @property
   def length(self) -> float:
      pass

   @property
   def width(self) -> float:
      pass

   @property
   def height(self) -> float:
      pass
