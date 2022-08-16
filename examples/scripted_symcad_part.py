#!/usr/bin/env python3

from __future__ import annotations
from PyFreeCAD.FreeCAD import FreeCAD, Part
from symcad.core.SymPart import SymPart
from typing import Dict, Tuple, Union
from sympy import Symbol, Expr

class MyCustomBox(SymPart):

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: float):
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'length', Symbol(self.name + '_length'))
      setattr(self.geometry, 'width', Symbol(self.name + '_width'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      thickness_mm = 1000.0 * params['thickness']
      outer_length_mm = 1000.0 * params['length']
      outer_width_mm = 1000.0 * params['width']
      outer_height_mm = 1000.0 * params['height']
      inner_length_mm = outer_length_mm - (2.0 * thickness_mm)
      inner_width_mm = outer_width_mm - (2.0 * thickness_mm)
      inner_height_mm = outer_height_mm - (2.0 * thickness_mm)
      outer = Part.makeBox(outer_length_mm, outer_width_mm, outer_height_mm)
      inner = Part.makeBox(inner_length_mm, inner_width_mm, inner_height_mm,
                           FreeCAD.Vector(thickness_mm, thickness_mm, thickness_mm))
      return outer if fully_displace else outer.cut(inner)


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
