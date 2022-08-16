#!/usr/bin/env python3

from __future__ import annotations
from PyFreeCAD.FreeCAD import FreeCAD, Part
from symcad.core.SymPart import SymPart
from symcad.core.Assembly import Assembly
from typing import Dict, List, Tuple, Union
from sympy import Symbol, Expr
from functools import partial
import math

class PitchControl(SymPart):

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str, material_density_kg_m3: float):
      cad_creation_partial = partial(self.__create_cad__, self)
      super().__init__(identifier, cad_creation_partial, None, material_density_kg_m3)
      setattr(self.geometry, 'trim_weight_radius', Symbol(self.name + '_trim_weight_radius'))
      setattr(self.geometry, 'trim_weight_length', Symbol(self.name + '_trim_weight_length'))
      setattr(self.geometry, 'container_length', Symbol(self.name + '_container_length'))
      setattr(self.geometry, 'container_thickness', Symbol(self.name + '_container_thickness'))


   # CAD generation function ----------------------------------------------------------------------

   @staticmethod
   def __create_cad__(self: SymPart, params: Dict[str, float], _fully_displace: bool) -> Part.Solid:
      container_thickness_mm = 1000.0 * params['container_thickness']
      container_outer_length_mm = 1000.0 * params['container_length']
      container_inner_length_mm = container_outer_length_mm - (2 * container_thickness_mm)
      trim_weight_radius_mm = 1000.0 * params['trim_weight_radius']
      trim_weight_length_mm = 1000.0 * params['trim_weight_length']
      container_outer_radius_mm = trim_weight_radius_mm + container_thickness_mm
      trim_weight = Part.makeCylinder(trim_weight_radius_mm, trim_weight_length_mm)
      container_outer = Part.makeCylinder(container_outer_radius_mm, container_outer_length_mm)
      container_inner = Part.makeCylinder(trim_weight_radius_mm, container_inner_length_mm)
      container_inner.Placement.Base.z = container_thickness_mm
      if 'pitch_down' in self.current_states:
         trim_weight.Placement.Base.z = container_thickness_mm
      elif 'pitch_up' in self.current_states:
         trim_weight.Placement.Base.z = \
            container_outer_length_mm - container_thickness_mm - trim_weight_length_mm
      else:
         trim_weight.Placement.Base.z = (container_outer_length_mm - trim_weight_length_mm) / 2
      pitch_control = container_outer.cut(container_inner).fuse(trim_weight)
      pitch_control.Placement.Rotation = FreeCAD.Rotation(0, 90, 0)
      return Part.Solid(pitch_control)


   # Geometry setter and listing of valid states --------------------------------------------------

   def set_geometry(self, *, trim_weight_radius_m: Union[float, None],
                             trim_weight_length_m: Union[float, None],
                             container_length_m: Union[float, None],
                             container_thickness_m: Union[float, None]) -> PitchControl:
      self.geometry.set(trim_weight_radius=trim_weight_radius_m,
                        trim_weight_length=trim_weight_length_m,
                        container_length=container_length_m,
                        container_thickness=container_thickness_m)
      return self

   def get_valid_states(self) -> List[str]:
      return ['pitch_down', 'pitch_up', 'pitch_neutral']


   # Geometric properties -------------------------------------------------------------------------

   @property
   def material_volume(self) -> Union[float, Expr]:
      return self.displaced_volume

   @property
   def displaced_volume(self) -> Union[float, Expr]:
      container_radius = self.geometry.trim_weight_radius + self.geometry.container_thickness
      container_inner_length = self.geometry.container_length - \
                               (2.0 * self.geometry.container_thickness)
      return math.pi * (
         (self.geometry.trim_weight_radius**2 * self.geometry.trim_weight_length) +
         (container_radius**2 * self.geometry.container_length) -
         (self.geometry.trim_weight_radius**2 * container_inner_length))

   @property
   def surface_area(self) -> Union[float, Expr]:
      container_radius = self.geometry.trim_weight_radius + self.geometry.container_thickness
      return (2.0 * math.pi * container_radius * self.geometry.container_length) + \
             (2.0 * math.pi * container_radius**2)

   @property
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      if 'pitch_down' in self.current_states:
         cg_x = self.geometry.container_thickness + (0.5 * self.geometry.trim_weight_length)
      elif 'pitch_up' in self.current_states:
         cg_x = self.geometry.container_length - self.geometry.container_thickness - \
                (0.5 * self.geometry.trim_weight_length)
      else:
         cg_x = 0.5 * self.geometry.container_length
      return (cg_x,
              self.geometry.container_thickness + self.geometry.trim_weight_radius,
              self.geometry.container_thickness + self.geometry.trim_weight_radius)

   @property
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      return self.unoriented_center_of_gravity

   @property
   def unoriented_length(self) -> Union[float, Expr]:
      return self.geometry.container_length

   @property
   def unoriented_width(self) -> Union[float, Expr]:
      return 2.0 * (self.geometry.trim_weight_radius + self.geometry.container_thickness)

   @property
   def unoriented_height(self) -> Union[float, Expr]:
      return self.unoriented_width


if __name__ == '__main__':

   # Create a pitch control component and output its valid custom states
   pitch_control = PitchControl('TestPitchControl', 2400.0)
   pitch_control.set_geometry(trim_weight_radius_m=0.25,
                              trim_weight_length_m=0.4,
                              container_length_m=1.0,
                              container_thickness_m=0.0025)
   print('Part Valid States: {}'.format(pitch_control.get_valid_states()))

   # Output the center of gravity of the part when in its various states
   pitch_control.set_state(['pitch_down'])
   print('Part Center of Gravity (pitch_down): {}'.format(pitch_control.unoriented_center_of_gravity))
   pitch_control.set_state(['pitch_neutral'])
   print('Part Center of Gravity (pitch_neutral): {}'.format(pitch_control.unoriented_center_of_gravity))
   pitch_control.set_state(['pitch_up'])
   print('Part Center of Gravity (pitch_up): {}'.format(pitch_control.unoriented_center_of_gravity))

   # Add two versions of this component to an assembly
   assembly = Assembly('CustomStateAssembly')
   pitch_control1 = PitchControl('PitchControlLeft', 2400.0)\
      .add_attachment_point('RightFront', x=0, y=1, z=0.5)\
      .set_geometry(trim_weight_radius_m=0.25,
                    trim_weight_length_m=0.4,
                    container_length_m=1.0,
                    container_thickness_m=0.0025)
   pitch_control2 = PitchControl('PitchControlRight', 2400.0)\
      .add_attachment_point('LeftFront', x=0, y=0, z=0.5)\
      .set_geometry(trim_weight_radius_m=0.2,
                    trim_weight_length_m=0.2,
                    container_length_m=0.6,
                    container_thickness_m=0.0025)
   pitch_control1.attach('RightFront', pitch_control2, 'LeftFront')
   pitch_control1.set_placement(placement=(0, 0, 0), local_origin=(0, 1, 0.5))
   assembly.add_part(pitch_control1)
   assembly.add_part(pitch_control2)

   # Output the center of gravity of the assembly when in its various states
   print('Assembly Valid States: {}'.format(assembly.get_valid_states()))
   assembly.set_state(['pitch_down'])
   print('Assembly Center of Gravity (pitch_down): {}'.format(assembly.center_of_gravity()))
   assembly.set_state(['pitch_neutral'])
   print('Assembly Center of Gravity (pitch_neutral): {}'.format(assembly.center_of_gravity()))
   assembly.set_state(['pitch_up'])
   print('Assembly Center of Gravity (pitch_up): {}'.format(assembly.center_of_gravity()))
