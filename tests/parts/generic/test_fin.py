#!/usr/bin/env python3

import math, os, sympy
from symcad.parts import Fin, SymPart

symbolic_identifier = 'fin_symbolic'
hybrid_identifier = 'fin_hybrid'
concrete_identifier = 'fin_concrete'

def test_construction(print_output: bool = False):

   # Construct a default instance of the shape
   shape_symbolic = Fin(symbolic_identifier)

   # Assert that the shape type is as expected
   assert issubclass(Fin, SymPart)
   assert isinstance(shape_symbolic, SymPart)
   assert isinstance(shape_symbolic, Fin)

   # Assert that the shape name is as expected
   assert shape_symbolic.name == symbolic_identifier

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.lower_length == sympy.Symbol(symbolic_identifier + '_lower_length')
   assert shape_symbolic.geometry.upper_length == sympy.Symbol(symbolic_identifier + '_upper_length')
   assert shape_symbolic.geometry.thickness == sympy.Symbol(symbolic_identifier + '_thickness')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Print constructed output if requested
   if print_output:
      print('\nSymbolic Constructed: {}'.format(shape_symbolic))


def test_setting(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = Fin(symbolic_identifier)
   shape_hybrid = Fin(hybrid_identifier).set_geometry(lower_length_m=None, upper_length_m=0.3, thickness_m=0.2, height_m=None)
   shape_concrete = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
                                            .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                            .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.lower_length == sympy.Symbol(symbolic_identifier + '_lower_length')
   assert shape_symbolic.geometry.upper_length == sympy.Symbol(symbolic_identifier + '_upper_length')
   assert shape_symbolic.geometry.thickness == sympy.Symbol(symbolic_identifier + '_thickness')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.lower_length == sympy.Symbol(hybrid_identifier + '_lower_length')
   assert shape_hybrid.geometry.upper_length == 0.3
   assert shape_hybrid.geometry.thickness == 0.2
   assert shape_hybrid.geometry.height == sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.lower_length == 1.0
   assert shape_concrete.geometry.upper_length == 0.3
   assert shape_concrete.geometry.thickness == 0.2
   assert shape_concrete.geometry.height == 1.2
   assert shape_concrete.orientation.roll == math.radians(20.0)
   assert shape_concrete.orientation.pitch == math.radians(31.0)
   assert shape_concrete.orientation.yaw == math.radians(40.0)

   # Print set output if requested
   if print_output:
      print('\nSymbolic Set: {}'.format(shape_symbolic))
      print('Hybrid Set: {}'.format(shape_hybrid))
      print('Concrete Set: {}'.format(shape_concrete))


def test_geometric_properties(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = Fin(symbolic_identifier)
   shape_hybrid = Fin(hybrid_identifier).set_geometry(lower_length_m=None, upper_length_m=0.3, thickness_m=0.2, height_m=None)
   shape_concrete = Fin(concrete_identifier, 2.0).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)

   # Assert that all concrete geometric properties are as expected
   cad_props = shape_concrete.get_cad_physical_properties(True)
   assert abs(cad_props['xlen'] - shape_concrete.unoriented_length) < 0.001
   assert abs(cad_props['ylen'] - shape_concrete.unoriented_width) < 0.001
   assert abs(cad_props['zlen'] - shape_concrete.unoriented_height) < 0.001
   assert abs(cad_props['cg_x'] - shape_concrete.unoriented_center_of_gravity[0]) < 0.001
   assert abs(cad_props['cg_y'] - shape_concrete.unoriented_center_of_gravity[1]) < 0.001
   assert abs(cad_props['cg_z'] - shape_concrete.unoriented_center_of_gravity[2]) < 0.001
   assert abs(cad_props['cb_x'] - shape_concrete.unoriented_center_of_buoyancy[0]) < 0.001
   assert abs(cad_props['cb_y'] - shape_concrete.unoriented_center_of_buoyancy[1]) < 0.001
   assert abs(cad_props['cb_z'] - shape_concrete.unoriented_center_of_buoyancy[2]) < 0.001
   assert abs(cad_props['min_x']) < 0.001
   assert abs(cad_props['min_y']) < 0.001
   assert abs(cad_props['min_z']) < 0.001
   assert abs(cad_props['mass'] - shape_concrete.mass) < 0.001
   assert abs(cad_props['material_volume'] - shape_concrete.material_volume) < 0.001
   assert abs(cad_props['displaced_volume'] - shape_concrete.displaced_volume) < 0.001
   assert abs(cad_props['surface_area'] - shape_concrete.surface_area) < 0.001

   # Print all symbolic geometric properties if requested
   if print_output:
      print('\nSymbolic Properties:\n')
      print('\tMass: {}'.format(shape_symbolic.mass))
      print('\tMaterial Volume: {}'.format(shape_symbolic.material_volume))
      print('\tDisplaced Volume: {}'.format(shape_symbolic.displaced_volume))
      print('\tSurface Area: {}'.format(shape_symbolic.surface_area))
      print('\tLength (Unoriented): {}'.format(shape_symbolic.unoriented_length))
      print('\tWidth (Unoriented): {}'.format(shape_symbolic.unoriented_width))
      print('\tHeight (Unoriented): {}'.format(shape_symbolic.unoriented_height))
      print('\tCenter of Gravity (Unoriented): {}'.format(shape_symbolic.unoriented_center_of_gravity))
      print('\tCenter of Buoyancy (Unoriented): {}'.format(shape_symbolic.unoriented_center_of_buoyancy))
      print('\tLength (Oriented): {}'.format(shape_symbolic.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_symbolic.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_symbolic.oriented_height))

   # Print all hybrid geometric properties if requested
   if print_output:
      print('\nHybrid Properties:\n')
      print('\tMass: {}'.format(shape_hybrid.mass))
      print('\tMaterial Volume: {}'.format(shape_hybrid.material_volume))
      print('\tDisplaced Volume: {}'.format(shape_hybrid.displaced_volume))
      print('\tSurface Area: {}'.format(shape_hybrid.surface_area))
      print('\tLength (Unoriented): {}'.format(shape_hybrid.unoriented_length))
      print('\tWidth (Unoriented): {}'.format(shape_hybrid.unoriented_width))
      print('\tHeight (Unoriented): {}'.format(shape_hybrid.unoriented_height))
      print('\tCenter of Gravity (Unoriented): {}'.format(shape_hybrid.unoriented_center_of_gravity))
      print('\tCenter of Buoyancy (Unoriented): {}'.format(shape_hybrid.unoriented_center_of_buoyancy))
      print('\tLength (Oriented): {}'.format(shape_hybrid.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_hybrid.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_hybrid.oriented_height))

   # Print all concrete geometric properties if requested
   if print_output:
      print('\nConcrete Properties:\n')
      print('\tMass: {}'.format(shape_concrete.mass))
      print('\tMaterial Volume: {}'.format(shape_concrete.material_volume))
      print('\tDisplaced Volume: {}'.format(shape_concrete.displaced_volume))
      print('\tSurface Area: {}'.format(shape_concrete.surface_area))
      print('\tLength (Unoriented): {}'.format(shape_concrete.unoriented_length))
      print('\tWidth (Unoriented): {}'.format(shape_concrete.unoriented_width))
      print('\tHeight (Unoriented): {}'.format(shape_concrete.unoriented_height))
      print('\tCenter of Gravity (Unoriented): {}'.format(shape_concrete.unoriented_center_of_gravity))
      print('\tCenter of Buoyancy (Unoriented): {}'.format(shape_concrete.unoriented_center_of_buoyancy))
      print('\tLength (Oriented): {}'.format(shape_concrete.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_concrete.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_concrete.oriented_height))


def test_oriented_properties(print_output: bool = False):

   # Test physical properties after part rotation
   shape_concrete = Fin(concrete_identifier, 2.0)\
      .set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
      .set_orientation(roll_deg=39.0, pitch_deg=-10.0, yaw_deg=30.0)\
      .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.5, 0.0))
   props = shape_concrete.get_cad_physical_properties()
   print(props)
   print(shape_concrete.oriented_length, shape_concrete.oriented_width, shape_concrete.oriented_height)
   assert abs(shape_concrete.oriented_length - props['xlen']) < 0.05
   assert abs(shape_concrete.oriented_width - props['ylen']) < 0.07
   assert abs(shape_concrete.oriented_height - props['zlen']) < 0.1
   assert abs(shape_concrete.oriented_center_of_gravity[0] - props['cg_x']) < 0.001 and \
          abs(shape_concrete.oriented_center_of_gravity[1] - props['cg_y']) < 0.001 and \
          abs(shape_concrete.oriented_center_of_gravity[2] - props['cg_z']) < 0.001
   assert abs(shape_concrete.oriented_center_of_buoyancy[0] - props['cb_x']) < 0.001 and \
          abs(shape_concrete.oriented_center_of_buoyancy[1] - props['cb_y']) < 0.001 and \
          abs(shape_concrete.oriented_center_of_buoyancy[2] - props['cb_z']) < 0.001

   # Print all oriented geometric properties if requested
   if print_output:
      print('\nOriented Properties:\n')
      print('\tLength (Oriented): {}'.format(shape_concrete.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_concrete.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_concrete.oriented_height))
      print('\tCenter of Gravity (Oriented): {}'.format(shape_concrete.oriented_center_of_gravity))
      print('\tCenter of Buoyancy (Oriented): {}'.format(shape_concrete.oriented_center_of_buoyancy))


def test_cad(_print_output: bool = False):

   # Construct concrete versions of the shape
   shape_concrete = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)
   shape_concrete_rolled = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
                                                   .set_orientation(roll_deg=20.0, pitch_deg=0.0, yaw_deg=0.0)
   shape_concrete_pitched = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
                                                    .set_orientation(roll_deg=0.0, pitch_deg=20.0, yaw_deg=0.0)
   shape_concrete_yawed = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
                                                  .set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=20.0)
   shape_concrete_rotated = Fin(concrete_identifier).set_geometry(lower_length_m=1.0, upper_length_m=0.3, thickness_m=0.2, height_m=1.2)\
                                                    .set_orientation(roll_deg=-20.0, pitch_deg=-20.0, yaw_deg=-20.0)

   # Export FreeCAD versions of the rotated shapes
   shape_concrete.export('fin.FCStd', 'freecad')
   shape_concrete_rolled.export('fin_rolled.FCStd', 'freecad')
   shape_concrete_pitched.export('fin_pitched.FCStd', 'freecad')
   shape_concrete_yawed.export('fin_yawed.FCStd', 'freecad')
   shape_concrete_rotated.export('fin_rotated.FCStd', 'freecad')
   os.remove('fin.FCStd')
   os.remove('fin_rolled.FCStd')
   os.remove('fin_pitched.FCStd')
   os.remove('fin_yawed.FCStd')
   os.remove('fin_rotated.FCStd')


if __name__ == '__main__':

   # Run through all test suites
   test_construction(True)
   test_setting(True)
   test_cad(True)
   test_geometric_properties(True)
   test_oriented_properties(True)
