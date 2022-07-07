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
from typing import List, Tuple, Union
from sympy import Expr
import math

def spherical_points(*, num_points: int,
                        radius: Union[float, Expr],
                        center_x: Union[float, Expr],
                        center_y: Union[float, Expr],
                        center_z: Union[float, Expr]) -> List[Tuple[float, float, float]]:
   points = []
   for i in range(1, num_points + 1):
      h = -1.0 + 2.0 * (i - 1) / (num_points - 1)
      theta = math.acos(h)
      phi = 0 if i == 1 or i == num_points else phi + (3.6 / math.sqrt(num_points * (1.0 - h**2)))
      points.append((center_x + (math.sin(phi) * math.sin(theta) * radius),
                     center_y + (math.cos(phi) * math.sin(theta) * radius),
                     center_z - (math.cos(theta) * radius)))
      phi %= (2.0 * math.pi)
   return points
