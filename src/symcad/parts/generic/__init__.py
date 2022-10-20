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
from typing import Callable, Union
from ...core.ML import NeuralNet
import abc, os

class GenericShape(SymPart, metaclass=abc.ABCMeta):
   """Base class from which all generic parametric shapes should derive."""

   def __init__(self, identifier: str,
                      cad_representation: Union[str, Callable],
                      properties_model: Union[str, NeuralNet, None],
                      material_density_kg_m3: float) -> None:
      """Initializes a generic parametric `SymPart`.

      Parameters
      ----------
      identifier : `str`
         Unique, identifying name for the `GenericShape`.
      cad_representation : `Union[str, Callable]`
         Either the path to a representative CAD model for the given `GenericShape` or a
         callable method that can create such a model.
      properties_model : `Union[str, NeuralNet, None]`
         Path to or instance of a neural network that may be evaluated to obtain the underlying
         geometric properties for the given `GenericShape`.
      material_density_kg_m3 : `float`
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier,
                       os.path.join('generic', cad_representation)
                          if isinstance(cad_representation, str) else
                       cad_representation,
                       os.path.join('generic', properties_model)
                          if properties_model and isinstance(properties_model, str) else
                       properties_model,
                       material_density_kg_m3)

from .Box import Box
from .Capsule import Capsule
from .Cone import Cone
from .Cuboid import Cuboid
from .Custom import Custom
from .Cylinder import Cylinder
from .EllipsoidalCap import EllipsoidalCap
from .EllipticCylinder import EllipticCylinder
from .EllipticPipe import EllipticPipe
from .Fin import Fin
from .Parallelepiped import Parallelepiped
from .Pipe import Pipe
from .Prism import Prism
from .Pyramid import Pyramid
from .Sphere import Sphere
from .SymmetricAirfoil import SymmetricAirfoil
from .Torus import Torus
