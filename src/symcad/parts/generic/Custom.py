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
from typing import Callable, Optional, Tuple, Union
from ...core.CAD import CadGeneral
from ...core.ML import NeuralNet
from sympy import Expr, Symbol
from . import GenericShape
from pathlib import Path

NOT_IMPLEMENTED_MESSAGE = 'The "{}" method is not implemented for non-concrete,\
                           parametric Custom parts with no underlying trained geometric models.'

class Custom(GenericShape):
   """Model representing a custom generic part.

   This class should be used to define a new type of CAD model from within an external library or
   application, without the need to alter the built-in library of parts within SymCAD.

   Regardless of whether an existing CAD model (parameteric or fixed-geometry) or a CAD creation
   function is used to create this part, SymCAD will automatically retrieve any geometric free
   parameters specified in the model and create symbols for them.
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, type_name: str,
                      identifier: str,
                      cad_representation: Union[str, Callable],
                      pretrained_geometric_properties_model: Union[str, None],
                      material_density_kg_m3: Optional[float] = 1.0,
                      auto_train_missing_property_model: bool = True) -> None:
      """Initializes a custom `GenericShape` part object.

      If the `Custom` part is parametric and requires a trained neural network to evaluate its
      geometric or mass properties, this network should be trained using the accompanying
      `NeuralNetTrainer` tool, and the full path to the resulting neural network model should be
      passed in using the `pretrained_geometric_properties_model` parameter. Alternately, a value
      of `None` may be passed in for this parameter, and a new model will automatically be
      trained if the `auto_train_missing_property_model` parameter is set to `True`.

      Parameters
      ----------
      type_name : `str`
         Name identifying the type of part of this object.
      identifier : `str`
         Unique identifying name for this instance of the object.
      cad_representation : `Union[str, Callable]`
         Either the path to a representative CAD model for the given part or a callable
         method that can create such a model.
      pretrained_geometric_properties_model : `Union[str, None]`
         Path to a neural network that represents the underlying geometric properties for
         the given `Custom` part, or `None` if no model is required.
      material_density_kg_m3 : `float`, optional, default=1.0
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      auto_train_missing_property_model : `bool`, default=True
         Whether to automatically train new a neural network model to evaluate the geometric
         properties of the `Custom` part.
      """
      super().__init__(identifier, cad_representation, None, material_density_kg_m3)
      free_params = CadGeneral.get_free_parameters_from_model(self.__cad__.cad_file_path, None) \
                       if isinstance(cad_representation, str) else \
                    CadGeneral.get_free_parameters_from_method(self.__cad__.creation_callback)
      self._is_concrete = len(free_params) == 0
      for param in free_params:
         setattr(self.geometry, param, Symbol(self.name + '_' + param))
      if not self._is_concrete:
         self.__neural_net__ = NeuralNet(pretrained_geometric_properties_model
                                            if pretrained_geometric_properties_model else
                                         Path('converted').joinpath(type_name + '.tar.xz'),
                                         self,
                                         auto_train_missing_property_model)


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, **kwargs) -> Custom:
      """Sets the physical geometry of the current `Custom` object.

      The `**kwargs` argument should include key-value pairs containing the name and desired
      concrete value for any geometric parameters of interest. In order to determine the parameters
      available, you should inspect the `geometry` attribute of the current `Custom` instance
      (e.g., `print(custom_shape.geometry)`).

      Parameters
      ----------
      **kwargs : `Dict`
         Set of named parameters that define the geometry of this Custom part. If the named
         parameter is missing or set to `None` for any geometric parameter, that parameter will be
         treated as a symbol.
      """
      free_params = []
      self.geometry.set(**kwargs)
      for key in self.geometry.__dict__:
         if key != 'name' and isinstance(getattr(self.geometry, key), Expr):
            free_params.append(key)
      self._is_concrete = len(free_params) == 0
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['material_volume']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('material_volume', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('material_volume'))

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['displaced_volume']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('displaced_volume', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('displaced_volume'))

   @property
   def surface_area(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['surface_area']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('surface_area', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('surface_area'))

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return (prop['cg_x'] - prop['min_x'],
                 prop['cg_y'] - prop['min_y'],
                 prop['cg_z'] - prop['min_z'])
      elif self.__neural_net__:
         return (self.__neural_net__.evaluate('cg_x', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_x', **self.geometry.as_dict()),
                 self.__neural_net__.evaluate('cg_y', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_y', **self.geometry.as_dict()),
                 self.__neural_net__.evaluate('cg_z', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_z', **self.geometry.as_dict()))
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('unoriented_center_of_gravity'))

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return (prop['cb_x'] - prop['min_x'],
                 prop['cb_y'] - prop['min_y'],
                 prop['cb_z'] - prop['min_z'])
      elif self.__neural_net__:
         return (self.__neural_net__.evaluate('cb_x', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_x', **self.geometry.as_dict()),
                 self.__neural_net__.evaluate('cb_y', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_y', **self.geometry.as_dict()),
                 self.__neural_net__.evaluate('cb_z', **self.geometry.as_dict()) - 
                    self.__neural_net__.evaluate('min_z', **self.geometry.as_dict()))
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('unoriented_center_of_buoyancy'))

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['xlen']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('xlen', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('unoriented_length'))

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['ylen']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('ylen', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('unoriented_width'))

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      if self._is_concrete:
         prop = self.__cad__.get_physical_properties(self.geometry.as_dict(),
                                                     (0.0, 0.0, 0.0),
                                                     (0.0, 0.0, 0.0),
                                                     self.material_density)
         return prop['zlen']
      elif self.__neural_net__:
         return self.__neural_net__.evaluate('zlen', **self.geometry.as_dict())
      else:
         raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE.format('unoriented_height'))
