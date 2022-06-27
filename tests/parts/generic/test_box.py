#!/usr/bin/env python3

import math, os, sympy
from symcad.parts import Box, SymPart

symbolic_identifier = 'box_symbolic'
hybrid_identifier = 'box_hybrid'
concrete_identifier = 'box_concrete'

def test_construction(print_output: bool = False):

   # Construct a default instance of the shape
   shape_symbolic = Box(symbolic_identifier)

   # Assert that the shape type is as expected
   assert issubclass(Box, SymPart)
   assert isinstance(shape_symbolic, SymPart)
   assert isinstance(shape_symbolic, Box)

   # Assert that the shape name is as expected
   assert shape_symbolic.name == symbolic_identifier

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.length == sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic.geometry.width == sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.geometry.thickness == sympy.Symbol(symbolic_identifier + '_thickness')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Print constructed output if requested
   if print_output:
      print('\nSymbolic Constructed: {}'.format(shape_symbolic))


def test_setting(print_output: bool = False):

   # Construct various versions of the shape
   shape_symbolic = Box(symbolic_identifier)
   shape_hybrid = Box(hybrid_identifier).set_geometry(length_m=1.0, width_m=None, height_m=3.0, thickness_m=0.01)
   shape_concrete = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                            .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                            .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Set all shape versions
   shape_symbolic.set_geometry(length_m=None, width_m=None, height_m=None, thickness_m=None)
   shape_hybrid.set_geometry(length_m=None, width_m=2.0, height_m=None, thickness_m=0.01)
   shape_concrete.set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)

   # Assert that all symbolic shape parameters are as expected
   assert shape_symbolic.geometry.length == sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic.geometry.width == sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.geometry.thickness == sympy.Symbol(symbolic_identifier + '_thickness')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.length == sympy.Symbol(hybrid_identifier + '_length')
   assert shape_hybrid.geometry.width == 2.0
   assert shape_hybrid.geometry.height == sympy.Symbol(hybrid_identifier + '_height')
   assert shape_hybrid.geometry.thickness == 0.01
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.length == 1.0
   assert shape_concrete.geometry.width == 2.0
   assert shape_concrete.geometry.height == 3.0
   assert shape_concrete.geometry.thickness == 0.01
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
   shape_symbolic = Box(symbolic_identifier)
   shape_hybrid = Box(hybrid_identifier).set_geometry(length_m=1.0, width_m=None, height_m=3.0, thickness_m=0.01)
   shape_concrete = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                                 .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))\
                                                 .set_orientation(roll_deg=20.0, pitch_deg=31.0, yaw_deg=40.0)

   # Quadruple the shape dimensions in-place
   shape_symbolic *= 4.0
   shape_hybrid *= 4.0
   shape_concrete *= 4.0

   # Assert that the new shape dimensions are as expected
   assert shape_symbolic.geometry.length == 4.0 * sympy.Symbol(symbolic_identifier + '_length')
   assert shape_symbolic.geometry.width == 4.0 * sympy.Symbol(symbolic_identifier + '_width')
   assert shape_symbolic.geometry.height == 4.0 * sympy.Symbol(symbolic_identifier + '_height')
   assert shape_symbolic.geometry.thickness == 4.0 * sympy.Symbol(symbolic_identifier + '_thickness')
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.length == 4.0
   assert shape_hybrid.geometry.width == 4.0 * sympy.Symbol(hybrid_identifier + '_width')
   assert shape_hybrid.geometry.height == 12.0
   assert shape_hybrid.geometry.thickness == 0.04
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.length == 4.0
   assert shape_concrete.geometry.width == 8.0
   assert shape_concrete.geometry.height == 12.0
   assert shape_concrete.geometry.thickness == 0.04
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
   assert shape_symbolic.geometry.length == sympy.Symbol(symbolic_identifier + '_length') / 4.0
   assert shape_symbolic.geometry.width == sympy.Symbol(symbolic_identifier + '_width') / 4.0
   assert shape_symbolic.geometry.height == sympy.Symbol(symbolic_identifier + '_height') / 4.0
   assert shape_symbolic.geometry.thickness == sympy.Symbol(symbolic_identifier + '_thickness') / 4.0
   assert shape_symbolic.orientation.roll == 0.0
   assert shape_symbolic.orientation.pitch == 0.0
   assert shape_symbolic.orientation.yaw == 0.0

   # Assert that all hybrid shape parameters are as expected
   assert shape_hybrid.geometry.length == 1.0 / 4.0
   assert shape_hybrid.geometry.width == sympy.Symbol(hybrid_identifier + '_width') / 4.0
   assert shape_hybrid.geometry.height == 3.0 / 4.0
   assert shape_hybrid.geometry.thickness == 0.01 / 4.0
   assert shape_hybrid.orientation.roll == 0.0
   assert shape_hybrid.orientation.pitch == 0.0
   assert shape_hybrid.orientation.yaw == 0.0

   # Assert that all concrete shape parameters are as expected
   assert shape_concrete.geometry.length == 1.0 / 4.0
   assert shape_concrete.geometry.width == 2.0 / 4.0
   assert shape_concrete.geometry.height == 3.0 / 4.0
   assert shape_concrete.geometry.thickness == 0.01 / 4.0
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
   shape_symbolic = Box(symbolic_identifier)
   shape_hybrid = Box(hybrid_identifier).set_geometry(length_m=1.0, width_m=None, height_m=3.0, thickness_m=0.01)
   shape_concrete = Box(concrete_identifier, 2.0).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)

   # Assert that all concrete geometric properties are as expected
   cad_props = shape_concrete.get_cad_physical_properties()
   assert abs(cad_props['xlen'] - shape_concrete.unoriented_length) < 0.001
   assert abs(cad_props['ylen'] - shape_concrete.unoriented_width) < 0.001
   assert abs(cad_props['zlen'] - shape_concrete.unoriented_height) < 0.001
   assert abs(cad_props['xlen'] - shape_concrete.oriented_length) < 0.001
   assert abs(cad_props['ylen'] - shape_concrete.oriented_width) < 0.001
   assert abs(cad_props['zlen'] - shape_concrete.oriented_height) < 0.001
   assert abs(cad_props['cg_x'] - shape_concrete.center_of_gravity[0]) < 0.001
   assert abs(cad_props['cg_y'] - shape_concrete.center_of_gravity[1]) < 0.001
   assert abs(cad_props['cg_z'] - shape_concrete.center_of_gravity[2]) < 0.001
   assert abs(cad_props['cb_x'] - shape_concrete.center_of_buoyancy[0]) < 0.001
   assert abs(cad_props['cb_y'] - shape_concrete.center_of_buoyancy[1]) < 0.001
   assert abs(cad_props['cb_z'] - shape_concrete.center_of_buoyancy[2]) < 0.001
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
   shape_concrete = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)
   shape_concrete_rolled = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                                   .set_orientation(roll_deg=20.0, pitch_deg=0.0, yaw_deg=0.0)
   shape_concrete_pitched = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                                    .set_orientation(roll_deg=0.0, pitch_deg=20.0, yaw_deg=0.0)
   shape_concrete_yawed = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                                  .set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=20.0)
   shape_concrete_rotated = Box(concrete_identifier).set_geometry(length_m=1.0, width_m=2.0, height_m=3.0, thickness_m=0.01)\
                                                    .set_orientation(roll_deg=-20.0, pitch_deg=-20.0, yaw_deg=-20.0)

   # Export FreeCAD versions of the rotated shapes
   shape_concrete.export('box.FCStd', 'freecad')
   shape_concrete_rolled.export('box_rolled.FCStd', 'freecad')
   shape_concrete_pitched.export('box_pitched.FCStd', 'freecad')
   shape_concrete_yawed.export('box_yawed.FCStd', 'freecad')
   shape_concrete_rotated.export('box_rotated.FCStd', 'freecad')
   os.remove('box.FCStd')
   os.remove('box_rolled.FCStd')
   os.remove('box_pitched.FCStd')
   os.remove('box_yawed.FCStd')
   os.remove('box_rotated.FCStd')


if __name__ == '__main__':

   # Run through all test suites
   test_construction(True)
   test_setting(True)
   test_built_ins(True)
   test_cad(True)
   test_geometric_properties(True)