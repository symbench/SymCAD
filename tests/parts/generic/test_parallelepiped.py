#!/usr/bin/env python3

import math, os, sympy
from symcad.parts import Parallelepiped, SymPart

symbolic_identifier = 'parallelepiped_symbolic'
hybrid_identifier = 'parallelepiped_hybrid'
concrete_identifier = 'parallelepiped_concrete'

def test_construction(print_output: bool = False):

   # Construct a default instance of the shape
   shape_symbolic = Parallelepiped(symbolic_identifier)

   # Assert that the shape type is as expected
   assert issubclass(Parallelepiped, SymPart)
   assert isinstance(shape_symbolic, SymPart)
   assert isinstance(shape_symbolic, Parallelepiped)

   # Assert that the shape name is as expected
   assert shape_symbolic.name == symbolic_identifier

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.length == sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic.geometry.width == sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.geometry.lh_angle == sympy.Symbol(symbolic_identifier + '_lh_angle')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Print constructed output if requested
   if print_output:
      print('\nSymbolic Constructed: {}'.format(shape_symbolic))


def test_setting(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = Parallelepiped(symbolic_identifier)
   shape_hybrid = Parallelepiped(hybrid_identifier).set_geometry(length_m=3.0, width_m=None, height_m=None, length_height_angle_rad=math.radians(80.0))
   shape_concrete = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                       .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                                       .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Set all shape versions
   shape_symbolic.set_geometry(length_m=None, width_m=None, height_m=None, length_height_angle_rad=None)
   shape_hybrid.set_geometry(length_m=3.0, width_m=None, height_m=None, length_height_angle_rad=math.radians(80.0))
   shape_concrete.set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.length == sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic.geometry.width == sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.geometry.lh_angle == sympy.Symbol(symbolic_identifier + '_lh_angle')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.length == 3.0
   assert shape_hybrid.geometry.width == sympy.Symbol(hybrid_identifier + '_width')
   assert shape_hybrid.geometry.height == sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid.geometry.lh_angle == math.radians(80.0)
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.length == 3.0
   assert shape_concrete.geometry.width == 2.0
   assert shape_concrete.geometry.height == 1.0
   assert shape_concrete.geometry.lh_angle == math.radians(80.0)
   assert shape_concrete.orientation.roll == math.radians(20.0)
   assert shape_concrete.orientation.pitch == math.radians(31.0)
   assert shape_concrete.orientation.yaw == math.radians(40.0)

   # Print set output if requested
   if print_output:
      print('\nSymbolic Set: {}'.format(shape_symbolic))
      print('Hybrid Set: {}'.format(shape_hybrid))
      print('Concrete Set: {}'.format(shape_concrete))


def test_built_ins(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic_math = Parallelepiped(symbolic_identifier)
   shape_hybrid_math = Parallelepiped(hybrid_identifier).set_geometry(length_m=3.0, width_m=None, height_m=None, length_height_angle_rad=math.radians(80.0))
   shape_concrete_math = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                            .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                                            .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Quadruple the shape dimensions in-place
   shape_symbolic_math *= 4.0
   shape_hybrid_math *= 4.0
   shape_concrete_math *= 4.0

   # Assert that the new shape dimensions are as expected
   assert shape_symbolic_math.geometry.length == 4.0 * sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic_math.geometry.width == 4.0 * sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic_math.geometry.height == 4.0 * sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic_math.geometry.lh_angle == sympy.Symbol(symbolic_identifier + '_lh_angle')
   assert shape_symbolic_math.orientation.roll == 0.0
   assert shape_symbolic_math.orientation.pitch == 0.0
   assert shape_symbolic_math.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid_math.geometry.length == 12.0
   assert shape_hybrid_math.geometry.width == 4.0 * sympy.Symbol(hybrid_identifier + '_width')
   assert shape_hybrid_math.geometry.height == 4.0 * sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid_math.geometry.lh_angle == math.radians(80.0)
   assert shape_hybrid_math.orientation.roll == 0.0
   assert shape_hybrid_math.orientation.pitch == 0.0
   assert shape_hybrid_math.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete_math.geometry.length == 12.0
   assert shape_concrete_math.geometry.width == 8.0
   assert shape_concrete_math.geometry.height == 4.0
   assert shape_concrete_math.geometry.lh_angle == math.radians(80.0)
   assert shape_concrete_math.orientation.roll == math.radians(20.0)
   assert shape_concrete_math.orientation.pitch == math.radians(31.0)
   assert shape_concrete_math.orientation.yaw == math.radians(40.0)

   # Print mutated output if requested
   if print_output:
      print('\nSymbolic Quadrupling In-Place: {}'.format(shape_symbolic_math))
      print('Hybrid Quadrupling In-Place: {}'.format(shape_hybrid_math))
      print('Concrete Quadrupling In-Place: {}'.format(shape_concrete_math))

   # Quarter the shape dimensions in-place
   shape_symbolic_math /= 16.0
   shape_hybrid_math /= 16.0
   shape_concrete_math /= 16.0

   # Assert that the new shape dimensions are as expected
   assert shape_symbolic_math.geometry.length == sympy.Symbol(symbolic_identifier + '_length') / 4.0
   assert shape_symbolic_math.geometry.width == sympy.Symbol(symbolic_identifier + '_width') / 4.0
   assert shape_symbolic_math.geometry.height == sympy.Symbol(symbolic_identifier + '_height') / 4.0
   assert shape_symbolic_math.geometry.lh_angle == sympy.Symbol(symbolic_identifier + '_lh_angle')
   assert shape_symbolic_math.orientation.roll == 0.0
   assert shape_symbolic_math.orientation.pitch == 0.0
   assert shape_symbolic_math.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid_math.geometry.length == 3.0 / 4.0
   assert shape_hybrid_math.geometry.width == sympy.Symbol(hybrid_identifier + '_width') / 4.0
   assert shape_hybrid_math.geometry.height == sympy.Symbol(hybrid_identifier + '_height') / 4.0
   assert shape_hybrid_math.geometry.lh_angle == math.radians(80.0)
   assert shape_hybrid_math.orientation.roll == 0.0
   assert shape_hybrid_math.orientation.pitch == 0.0
   assert shape_hybrid_math.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete_math.geometry.length == 3.0 / 4.0
   assert shape_concrete_math.geometry.width == 2.0 / 4.0
   assert shape_concrete_math.geometry.height == 1.0 / 4.0
   assert shape_concrete_math.geometry.lh_angle == math.radians(80.0)
   assert shape_concrete_math.orientation.roll == math.radians(20.0)
   assert shape_concrete_math.orientation.pitch == math.radians(31.0)
   assert shape_concrete_math.orientation.yaw == math.radians(40.0)

   # Print mutated output if requested
   if print_output:
      print('\nSymbolic Halving In-Place: {}'.format(shape_symbolic_math))
      print('Hybrid Halving In-Place: {}'.format(shape_hybrid_math))
      print('Concrete Halving In-Place: {}'.format(shape_concrete_math))


def test_geometric_properties(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = Parallelepiped(symbolic_identifier)
   shape_hybrid = Parallelepiped(hybrid_identifier).set_geometry(length_m=3.0, width_m=None, height_m=None, length_height_angle_rad=math.radians(80.0))
   shape_concrete = Parallelepiped(concrete_identifier, 2.0).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))

   # Assert that all concrete geometric properties are as expected
   cad_props = shape_concrete.get_cad_physical_properties()
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
   assert abs(cad_props['surface_area'] - shape_concrete.surface_area) < 0.1

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


def test_oriented_properties(print_output: bool = False):

   # Test physical properties after part rotation
   shape_concrete = Parallelepiped(concrete_identifier, 2.0)\
      .set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
      .set_orientation(roll_deg=39.0, pitch_deg=-10.0, yaw_deg=30.0)\
      .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.5, 0.0))
   props = shape_concrete.get_cad_physical_properties()
   # TODO: Fix oriented length/width/height
   #assert abs(shape_concrete.oriented_length - props['xlen']) < 0.001
   #assert abs(shape_concrete.oriented_width - props['ylen']) < 0.001
   #assert abs(shape_concrete.oriented_height - props['zlen']) < 0.001
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
   shape_concrete = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))
   shape_concrete_rolled = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                               .set_orientation(roll_deg=20.0, pitch_deg=0.0, yaw_deg=0.0)
   shape_concrete_pitched = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                               .set_orientation(roll_deg=0.0, pitch_deg=20.0, yaw_deg=0.0)
   shape_concrete_yawed = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                             .set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=20.0)
   shape_concrete_rotated = Parallelepiped(concrete_identifier).set_geometry(length_m=3.0, width_m=2.0, height_m=1.0, length_height_angle_rad=math.radians(80.0))\
                                                               .set_orientation(roll_deg=-20.0, pitch_deg=-20.0, yaw_deg=-20.0)

   # Export FreeCAD versions of the rotated shapes
   shape_concrete.export('parallelepiped.FCStd', 'freecad')
   shape_concrete_rolled.export('parallelepiped_rolled.FCStd', 'freecad')
   shape_concrete_pitched.export('parallelepiped_pitched.FCStd', 'freecad')
   shape_concrete_yawed.export('parallelepiped_yawed.FCStd', 'freecad')
   shape_concrete_rotated.export('parallelepiped_rotated.FCStd', 'freecad')
   os.remove('parallelepiped.FCStd')
   os.remove('parallelepiped_rolled.FCStd')
   os.remove('parallelepiped_pitched.FCStd')
   os.remove('parallelepiped_yawed.FCStd')
   os.remove('parallelepiped_rotated.FCStd')


if __name__ == '__main__':

   # Run through all test suites
   test_construction(True)
   test_setting(True)
   test_built_ins(True)
   test_cad(True)
   test_geometric_properties(True)
   test_oriented_properties(True)
