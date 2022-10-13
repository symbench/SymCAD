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
from typing import Tuple, Union
from . import FixedPart
from sympy import Expr

class TecnadyneModel2050Thruster(FixedPart):
   """Model representing a Tecnadyne Model 2050 thruster.

   By default, the part is oriented in the following way:

   ![TecnadyneModel2050Thruster](https://symbench.github.io/SymCAD/images/TecnadyneModel2050Thruster.png)
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str) -> None:
      """Initializes the Tecnadyne Model 2050 thruster fixed-geometry part.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      """
      super().__init__(identifier, 'thrusters/Tecnadyne_Model_2050.FCStd', 7828.8)


   # Geometric properties -------------------------------------------------------------------------

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return self.__cad_props__['cg_x'], 0.5 * self.unoriented_width, 0.5 * self.unoriented_height

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.__cad_props__['cb_x'], 0.5 * self.unoriented_width, 0.5 * self.unoriented_height

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 0.1391

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.unoriented_width
