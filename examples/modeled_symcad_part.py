#!/usr/bin/env python3

from __future__ import annotations
from symcad.core.SymPart import SymPart
from typing import Tuple, Union
from sympy import Symbol, Expr
from pathlib import Path

class MyCustomBox(SymPart):

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: float):
      model_path = Path(__file__).parent.joinpath('MyCustomBox.FCStd')
      super().__init__(identifier,
                       str(model_path.absolute().resolve()),
                       None,
                       material_density_kg_m3)
      setattr(self.geometry, 'length', Symbol(self.name + '_length'))
      setattr(self.geometry, 'width', Symbol(self.name + '_width'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # Geometry setter ------------------------------------------------------------------------------

   def set_geometry(self, *, length_m: Union[float, None],
                             width_m: Union[float, None],
                             height_m: Union[float, None],
                             thickness_m: Union[float, None]) -> MyCustomBox:
      self.geometry.set(length=length_m, width=width_m, height=height_m, thickness=thickness_m)
      return self


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['material_volume']

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['displaced_volume']

   @property
   def surface_area(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['surface_area']

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      return (self.get_cad_physical_properties()['cg_x'],
              self.get_cad_physical_properties()['cg_y'],
              self.get_cad_physical_properties()['cg_z'])

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return (self.get_cad_physical_properties()['cb_x'],
              self.get_cad_physical_properties()['cb_y'],
              self.get_cad_physical_properties()['cb_z'])

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['xlen']

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['ylen']

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.get_cad_physical_properties()['zlen']
