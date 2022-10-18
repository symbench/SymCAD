#!/usr/bin/env python3

from PyFreeCAD.FreeCAD import FreeCAD, Part
from symcad.parts import Custom
from typing import Dict
import random


def create_custom_part(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
   thickness_mm = 1000.0 * params['thickness']
   height_mm = 1000.0 * params['height']
   outer_radius_mm = 1000.0 * params['radius']
   inner_radius_mm = outer_radius_mm - thickness_mm
   outer_cylinder = Part.makeCylinder(outer_radius_mm, height_mm)
   if fully_displace:
      return outer_cylinder
   else:
      inner_cylinder = Part.makeCylinder(inner_radius_mm, height_mm)
      return outer_cylinder.cut(inner_cylinder)


if __name__ == '__main__':

   scripted_part = Custom('ScriptedCustomPart', 'test_part', create_custom_part, None, 1000.0)


   for _ in range(100):
      radius = random.random()
      height = random.random()
      thickness = random.random() * 0.02
      try:
         scripted_part.set_geometry(radius=radius, height=height, thickness=thickness)
         test_val = scripted_part.unoriented_center_of_gravity[1]
         real_val = scripted_part.get_cad_physical_properties()['cg_y']
         print('Rad = {}, Ht = {}, T = {} - Real Value: {}, Estimated: {}, Diff: {}'.format(radius, height, thickness, real_val, test_val, test_val - real_val))
      except Exception:
         continue

