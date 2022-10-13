#!/usr/bin/env python3

import os
from symcad.parts import SymPart, TecnadyneModel8050Thruster

shape_identifier = 'part_concrete'

def test_construction(print_output: bool = False):

   # Construct a default instance of the shape
   shape = TecnadyneModel8050Thruster(shape_identifier)

   # Assert that the shape type is as expected
   assert issubclass(TecnadyneModel8050Thruster, SymPart)
   assert isinstance(shape, SymPart)
   assert isinstance(shape, TecnadyneModel8050Thruster)

   # Assert that the shape name is as expected
   assert shape.name == shape_identifier

   # Print constructed output if requested
   if print_output:
      print('\nSymbolic Constructed: {}'.format(shape))


def test_geometric_properties(print_output: bool = False):

   # Construct a default instance of the shape
   shape = TecnadyneModel8050Thruster(shape_identifier)

   # Assert that all concrete geometric properties are as expected
   cad_props = shape.get_cad_physical_properties(True)
   assert abs(cad_props['xlen'] - shape.unoriented_length) < 0.001
   assert abs(0.1422 - shape.unoriented_width) < 0.001
   assert abs(0.1422 - shape.unoriented_height) < 0.001
   assert abs(cad_props['cg_x'] - shape.unoriented_center_of_gravity[0]) < 0.001
   assert abs(0.5 * 0.1422 - shape.unoriented_center_of_gravity[1]) < 0.001
   assert abs(0.5 * 0.1422 - shape.unoriented_center_of_gravity[2]) < 0.001
   assert abs(cad_props['cb_x'] - shape.unoriented_center_of_buoyancy[0]) < 0.001
   assert abs(0.5 * 0.1422 - shape.unoriented_center_of_buoyancy[1]) < 0.001
   assert abs(0.5 * 0.1422 - shape.unoriented_center_of_buoyancy[2]) < 0.001
   assert abs(cad_props['min_x']) < 0.001
   assert abs(cad_props['min_y']) < 0.001
   assert abs(cad_props['min_z']) < 0.001
   assert abs(cad_props['mass'] - shape.mass) < 0.001
   assert abs(shape.mass - 47.0) < 0.001
   assert abs(shape.mass - (shape.displaced_volume * 1027.0) - 31.772) < 0.001
   assert abs(cad_props['material_volume'] - shape.material_volume) < 0.001
   assert abs(cad_props['displaced_volume'] - shape.displaced_volume) < 0.001

   # Print all concrete geometric properties if requested
   if print_output:
      print('\nConcrete Properties:\n')
      print('\tMass: {}'.format(shape.mass))
      print('\tMaterial Volume: {}'.format(shape.material_volume))
      print('\tDisplaced Volume: {}'.format(shape.displaced_volume))
      print('\tSurface Area: {}'.format(shape.surface_area))
      print('\tLength (Unoriented): {}'.format(shape.unoriented_length))
      print('\tWidth (Unoriented): {}'.format(shape.unoriented_width))
      print('\tHeight (Unoriented): {}'.format(shape.unoriented_height))
      print('\tCenter of Gravity (Unoriented): {}'.format(shape.unoriented_center_of_gravity))
      print('\tCenter of Buoyancy (Unoriented): {}'.format(shape.unoriented_center_of_buoyancy))


def test_oriented_properties(print_output: bool = False):

   # Test physical properties after part rotation
   shape = TecnadyneModel8050Thruster(shape_identifier)\
      .set_orientation(roll_deg=39.0, pitch_deg=-10.0, yaw_deg=30.0)\
      .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.5, 0.0))
   props = shape.get_cad_physical_properties(True)
   assert abs(shape.oriented_length - props['xlen']) < 0.001
   assert abs(shape.oriented_width - props['ylen']) < 0.001
   assert abs(shape.oriented_height - props['zlen']) < 0.001
   assert abs(shape.oriented_center_of_gravity[0] - props['cg_x']) < 0.001 and \
          abs(shape.oriented_center_of_gravity[1] - props['cg_y']) < 0.001 and \
          abs(shape.oriented_center_of_gravity[2] - props['cg_z']) < 0.001
   assert abs(shape.oriented_center_of_buoyancy[0] - props['cb_x']) < 0.001 and \
          abs(shape.oriented_center_of_buoyancy[1] - props['cb_y']) < 0.001 and \
          abs(shape.oriented_center_of_buoyancy[2] - props['cb_z']) < 0.001

   # Print all oriented geometric properties if requested
   if print_output:
      print('\nOriented Properties:\n')
      print('\tLength (Oriented): {}'.format(shape.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape.oriented_height))
      print('\tCenter of Gravity (Oriented): {}'.format(shape.oriented_center_of_gravity))
      print('\tCenter of Buoyancy (Oriented): {}'.format(shape.oriented_center_of_buoyancy))


def test_cad(_print_output: bool = False):

   # Construct concrete versions of the shape
   shape = TecnadyneModel8050Thruster(shape_identifier)
   shape_rolled = TecnadyneModel8050Thruster(shape_identifier)\
      .set_orientation(roll_deg=20.0, pitch_deg=0.0, yaw_deg=0.0)
   shape_pitched = TecnadyneModel8050Thruster(shape_identifier)\
      .set_orientation(roll_deg=0.0, pitch_deg=20.0, yaw_deg=0.0)
   shape_yawed = TecnadyneModel8050Thruster(shape_identifier)\
      .set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=20.0)
   shape_rotated = TecnadyneModel8050Thruster(shape_identifier)\
       .set_orientation(roll_deg=-20.0, pitch_deg=-20.0, yaw_deg=-20.0)

   # Export FreeCAD versions of the rotated shapes
   shape.export('shape.FCStd', 'freecad')
   shape_rolled.export('shape_rolled.FCStd', 'freecad')
   shape_pitched.export('shape_pitched.FCStd', 'freecad')
   shape_yawed.export('shape_yawed.FCStd', 'freecad')
   shape_rotated.export('shape_rotated.FCStd', 'freecad')
   os.remove('shape.FCStd')
   os.remove('shape_rolled.FCStd')
   os.remove('shape_pitched.FCStd')
   os.remove('shape_yawed.FCStd')
   os.remove('shape_rotated.FCStd')


if __name__ == '__main__':

   # Run through all test suites
   test_construction(True)
   test_cad(True)
   test_geometric_properties(True)
   test_oriented_properties(True)
