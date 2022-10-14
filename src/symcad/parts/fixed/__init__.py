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
from ...core.SymPart import SymPart
from typing import Callable, Tuple, Union
from sympy import Expr
import abc, os

class FixedPart(SymPart, metaclass=abc.ABCMeta):
   """Base class from which all fixed-geometry parts should derive."""

   def __init__(self, identifier: str,
                      cad_representation: Union[str, Callable],
                      material_density_kg_m3: float) -> None:
      """Initializes a fixed-geometry `SymPart`.

      Parameters
      ----------
      identifier : `str`
         Unique, identifying name for the `FixedPart`.
      cad_representation : `Union[str, Callable]`
         Either the path to a representative CAD model for the given `FixedPart` or a
         callable method that can create such a model.
      material_density_kg_m3 : `float`
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier,
                       os.path.join('fixed', cad_representation)
                          if isinstance(cad_representation, str) else
                       cad_representation,
                       None,
                       material_density_kg_m3)
      self.__cad_props__ = self.__cad__.get_physical_properties({},
                                                                (0.0, 0.0, 0.0),
                                                                (0.0, 0.0, 0.0),
                                                                self.material_density,
                                                                True)

   def set_geometry(self) -> FixedPart:
      """Unused dummy function for all fixed-geometry parts of type `FixedPart`."""
      return self

   def get_geometric_parameter_bounds(self, parameter: str) -> Tuple[float, float]:
      """Unused dummy function for all fixed-geometry parts of type `FixedPart`."""
      return 0, 0

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.__cad_props__['material_volume']

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return self.__cad_props__['displaced_volume']

   @property
   def surface_area(self) -> Union[float, Expr]:
      return self.__cad_props__['surface_area']

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return self.__cad_props__['cg_x'], self.__cad_props__['cg_y'], self.__cad_props__['cg_z']

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.__cad_props__['cb_x'], self.__cad_props__['cb_y'], self.__cad_props__['cb_z']

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.__cad_props__['xlen']

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.__cad_props__['ylen']

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.__cad_props__['zlen']


from .Garmin15HGpsReceiver import Garmin15HGpsReceiver
from .IridiumCore9523Radio import IridiumCore9523Radio
from .iXbluePhinsCompactC7Ins import iXbluePhinsCompactC7Ins
from .NortekDVL1000_4000mDvl import NortekDVL1000_4000mDvl
from .OceanBottomSeismometer import OceanBottomSeismometer
from .RaspberryPiZero2Computer import RaspberryPiZero2Computer
from .TecnadyneModel550Thruster import TecnadyneModel550Thruster
from .TecnadyneModel2050Thruster import TecnadyneModel2050Thruster
from .TecnadyneModel2051Thruster import TecnadyneModel2051Thruster
from .TecnadyneModel2061Thruster import TecnadyneModel2061Thruster
from .TecnadyneModel8050Thruster import TecnadyneModel8050Thruster
from .TeledyneBenthosATM926AcousticModem import TeledyneBenthosATM926AcousticModem
from .TeledyneTasman600kHzDvl import TeledyneTasman600kHzDvl
from .TridentSensorsDualGpsIridiumAntenna import TridentSensorsDualGpsIridiumAntenna
