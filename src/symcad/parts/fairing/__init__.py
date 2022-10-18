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

class FairingShape(SymPart, metaclass=abc.ABCMeta):
   """Base class from which all fairing shapes should derive."""

   def __init__(self, identifier: str,
                      cad_representation: Union[str, Callable],
                      properties_model: Union[str, NeuralNet, None],
                      material_density_kg_m3: float) -> None:
      """Initializes a fairing `SymPart`.

      Parameters
      ----------
      identifier : `str`
         Unique, identifying name for the `FairingShape`.
      cad_representation : `Union[str, Callable]`
         Either the path to a representative CAD model for the given `FairingShape` or a
         callable method that can create such a model.
      properties_model : `Union[str, NeuralNet, None]`
         Path to or instance of a neural network that may be evaluated to obtain the underlying
         geometric properties for the given `FairingShape`.
      material_density_kg_m3 : `float`
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__(identifier,
                       os.path.join('fairing', cad_representation)
                          if isinstance(cad_representation, str) else
                       cad_representation,
                       os.path.join('fairing', properties_model)
                          if properties_model and isinstance(properties_model, str) else
                       properties_model,
                       material_density_kg_m3)

from .CylinderWithConicalEnds import CylinderWithConicalEnds
