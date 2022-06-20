#!/usr/bin/env python3

import math, os, sympy
from symcad.parts import EllipsoidalCap, SymPart

symbolic_identifier = 'ellipsoidal_cap_symbolic'
hybrid_identifier = 'ellipsoidal_cap_hybrid'
concrete_identifier = 'ellipsoidal_cap_concrete'

def test_construction(print_output: bool = False):

   # Construct a default instance of the shape
   shape_symbolic = EllipsoidalCap(symbolic_identifier)

   # Assert that the shape type is as expected
   assert issubclass(EllipsoidalCap, SymPart)
   assert isinstance(shape_symbolic, SymPart)
   assert isinstance(shape_symbolic, EllipsoidalCap)

   # Assert that the shape name is as expected
   assert shape_symbolic.name == symbolic_identifier

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.major_radius == sympy.Symbol(symbolic_identifier + '_major_radius')
   assert shape_symbolic.geometry.minor_radius == sympy.Symbol(symbolic_identifier + '_minor_radius')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Print constructed output if requested
   if print_output:
      print('\nSymbolic Constructed: {}'.format(shape_symbolic))


def test_setting(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = EllipsoidalCap(symbolic_identifier)
   shape_hybrid = EllipsoidalCap(hybrid_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=None)
   shape_concrete = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                       .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                                       .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Set all shape versions
   shape_symbolic.set_geometry(major_radius_m=None, minor_radius_m=None, height_m=None)
   shape_hybrid.set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=None)
   shape_concrete.set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.major_radius == sympy.Symbol(symbolic_identifier + '_major_radius')
   assert shape_symbolic.geometry.minor_radius == sympy.Symbol(symbolic_identifier + '_minor_radius')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.major_radius == 1.5
   assert shape_hybrid.geometry.minor_radius == 0.5
   assert shape_hybrid.geometry.height == sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.major_radius == 1.5
   assert shape_concrete.geometry.minor_radius == 0.5
   assert shape_concrete.geometry.height == 0.3
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
   shape_symbolic = EllipsoidalCap(symbolic_identifier)
   shape_hybrid = EllipsoidalCap(hybrid_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=None)
   shape_concrete = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                       .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                                       .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Quadruple the shape dimensions in-place
   shape_symbolic *= 4.0
   shape_hybrid *= 4.0
   shape_concrete *= 4.0

   # Assert that the new shape dimensions are as expected
   assert shape_symbolic.geometry.major_radius == 4.0 * sympy.Symbol(symbolic_identifier + '_major_radius')
   assert shape_symbolic.geometry.minor_radius == 4.0 * sympy.Symbol(symbolic_identifier + '_minor_radius')
   assert shape_symbolic.geometry.height == 4.0 * sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.major_radius == 6.0
   assert shape_hybrid.geometry.minor_radius == 2.0
   assert shape_hybrid.geometry.height == 4.0 * sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.major_radius == 6.0
   assert shape_concrete.geometry.minor_radius == 2.0
   assert shape_concrete.geometry.height == 1.2
   assert shape_concrete.orientation.roll == math.radians(20.0)
   assert shape_concrete.orientation.pitch == math.radians(31.0)
   assert shape_concrete.orientation.yaw == math.radians(40.0)

   # Print mutated output if requested
   if print_output:
      print('\nSymbolic Quadrupling In-Place: {}'.format(shape_symbolic))
      print('Hybrid Quadrupling In-Place: {}'.format(shape_hybrid))
      print('Concrete Quadrupling In-Place: {}'.format(shape_concrete))

   # Quarter the shape dimensions in-place
   shape_symbolic /= 16.0
   shape_hybrid /= 16.0
   shape_concrete /= 16.0

   # Assert that the new shape dimensions are as expected
   assert shape_symbolic.geometry.major_radius == sympy.Symbol(symbolic_identifier + '_major_radius') / 4.0
   assert shape_symbolic.geometry.minor_radius == sympy.Symbol(symbolic_identifier + '_minor_radius') / 4.0
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height') / 4.0
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.major_radius == 1.5 / 4.0
   assert shape_hybrid.geometry.minor_radius == 0.5 / 4.0
   assert shape_hybrid.geometry.height == sympy.Symbol(hybrid_identifier + '_height') / 4.0
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.major_radius == 1.5 / 4.0
   assert shape_concrete.geometry.minor_radius == 0.5 / 4.0
   assert shape_concrete.geometry.height == 0.3 / 4.0
   assert shape_concrete.orientation.roll == math.radians(20.0)
   assert shape_concrete.orientation.pitch == math.radians(31.0)
   assert shape_concrete.orientation.yaw == math.radians(40.0)

   # Print mutated output if requested
   if print_output:
      print('\nSymbolic Halving In-Place: {}'.format(shape_symbolic))
      print('Hybrid Halving In-Place: {}'.format(shape_hybrid))
      print('Concrete Halving In-Place: {}'.format(shape_concrete))


def test_geometric_properties(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = EllipsoidalCap(symbolic_identifier)
   shape_hybrid = EllipsoidalCap(hybrid_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=None)
   shape_concrete = EllipsoidalCap(concrete_identifier, 2.0).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)

   # Assert that all concrete geometric properties are as expected
   cad_props = shape_concrete.get_cad_physical_properties()
   assert abs(cad_props['xlen'] - shape_concrete.unoriented_length) < 0.001
   assert abs(cad_props['ylen'] - shape_concrete.unoriented_width) < 0.001
   assert abs(cad_props['zlen'] - shape_concrete.unoriented_height) < 0.001
   assert abs(cad_props['xlen'] - shape_concrete.oriented_length) < 0.001
   assert abs(cad_props['ylen'] - shape_concrete.oriented_width) < 0.001
   assert abs(cad_props['zlen'] - shape_concrete.oriented_height) < 0.001
   assert abs(cad_props['cg_x'] - shape_concrete.center_of_gravity[0]) < 0.01
   assert abs(cad_props['cg_y'] - shape_concrete.center_of_gravity[1]) < 0.01
   assert abs(cad_props['cg_z'] - shape_concrete.center_of_gravity[2]) < 0.01
   assert abs(cad_props['cb_x'] - shape_concrete.center_of_buoyancy[0]) < 0.01
   assert abs(cad_props['cb_y'] - shape_concrete.center_of_buoyancy[1]) < 0.01
   assert abs(cad_props['cb_z'] - shape_concrete.center_of_buoyancy[2]) < 0.01
   assert abs(cad_props['mass'] - shape_concrete.mass) < 0.02
   assert abs(cad_props['material_volume'] - shape_concrete.material_volume) < 0.01
   assert abs(cad_props['displaced_volume'] - shape_concrete.displaced_volume) < 0.01
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
      print('\tLength (Oriented): {}'.format(shape_symbolic.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_symbolic.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_symbolic.oriented_height))
      print('\tCenter of Gravity: {}'.format(shape_symbolic.center_of_gravity))
      print('\tCenter of Buoyancy: {}'.format(shape_symbolic.center_of_buoyancy))

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
      print('\tLength (Oriented): {}'.format(shape_hybrid.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_hybrid.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_hybrid.oriented_height))
      print('\tCenter of Gravity: {}'.format(shape_hybrid.center_of_gravity))
      print('\tCenter of Buoyancy: {}'.format(shape_hybrid.center_of_buoyancy))

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
      print('\tLength (Oriented): {}'.format(shape_concrete.oriented_length))
      print('\tWidth (Oriented): {}'.format(shape_concrete.oriented_width))
      print('\tHeight (Oriented): {}'.format(shape_concrete.oriented_height))
      print('\tCenter of Gravity: {}'.format(shape_concrete.center_of_gravity))
      print('\tCenter of Buoyancy: {}'.format(shape_concrete.center_of_buoyancy))


def test_cad(_print_output: bool = False):

   # Construct concrete versions of the shape
   shape_concrete = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)
   shape_concrete_rolled = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                              .set_orientation(roll_deg=20.0, pitch_deg=0.0, yaw_deg=0.0)
   shape_concrete_pitched = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                               .set_orientation(roll_deg=0.0, pitch_deg=20.0, yaw_deg=0.0)
   shape_concrete_yawed = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                             .set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=20.0)
   shape_concrete_rotated = EllipsoidalCap(concrete_identifier).set_geometry(major_radius_m=1.5, minor_radius_m=0.5, height_m=0.3)\
                                                               .set_orientation(roll_deg=-20.0, pitch_deg=-20.0, yaw_deg=-20.0)

   # Export FreeCAD versions of the rotated shapes
   shape_concrete.export('ellipsoidal_cap.FCStd', 'freecad')
   shape_concrete_rolled.export('ellipsoidal_cap_rolled.FCStd', 'freecad')
   shape_concrete_pitched.export('ellipsoidal_cap_pitched.FCStd', 'freecad')
   shape_concrete_yawed.export('ellipsoidal_cap_yawed.FCStd', 'freecad')
   shape_concrete_rotated.export('ellipsoidal_cap_rotated.FCStd', 'freecad')
   os.remove('ellipsoidal_cap.FCStd')
   os.remove('ellipsoidal_cap_rolled.FCStd')
   os.remove('ellipsoidal_cap_pitched.FCStd')
   os.remove('ellipsoidal_cap_yawed.FCStd')
   os.remove('ellipsoidal_cap_rotated.FCStd')


if __name__ == '__main__':

   # Run through all test suites
   test_construction(True)
   test_setting(True)
   test_built_ins(True)
   test_cad(True)
   test_geometric_properties(True)
