#!/usr/bin/env python3

from symcad.core import Coordinate, Assembly
from symcad.parts.endcaps import FlangedFlatPlate
from symcad.parts.generic import Cylinder, Pipe, Sphere
import os

def test_assembly_no_attachments(retain_output: bool):

   # Create an assembly with no attachments
   assembly = Assembly('AssemblyNoAttachments')
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)
   center_pipe = Pipe('Center', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   sphere = Sphere('RandomSphere', 1000.0)

   # Test exporting the assembly using a symbolic lookup dictionary
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   concrete_params = {
      'FrontEndcap_origin_x': 0.0,
      'FrontEndcap_origin_y': 0.5,
      'FrontEndcap_origin_z': 0.0,
      'FrontEndcap_placement_x': 0.08,
      'FrontEndcap_placement_y': 0.0,
      'FrontEndcap_placement_z': 0.0,
      'FrontEndcap_radius': 0.22,
      'FrontEndcap_thickness': 0.08,
      'Center_origin_x': 1.0,
      'Center_origin_y': 0.5,
      'Center_origin_z': 0.0,
      'Center_placement_x': 0.08,
      'Center_placement_y': 0.0,
      'Center_placement_z': 0.0,
      'Center_radius': 0.22,
      'Center_height': 0.6,
      'Center_thickness': 0.0025,
      'RearEndcap_origin_x': 1.0,
      'RearEndcap_origin_y': 0.5,
      'RearEndcap_origin_z': 0.0,
      'RearEndcap_placement_x': 0.68,
      'RearEndcap_placement_y': 0.0,
      'RearEndcap_placement_z': 0.0,
      'RearEndcap_radius': 0.22,
      'RearEndcap_thickness': 0.08,
      'RandomSphere_origin_x': 0.0,
      'RandomSphere_origin_y': 0.5,
      'RandomSphere_origin_z': 0.5,
      'RandomSphere_placement_x': 1.0,
      'RandomSphere_placement_y': 0.0,
      'RandomSphere_placement_z': 0.22,
      'RandomSphere_radius': 0.2
   }
   assembly.make_concrete(concrete_params).export('assembly_no_attachment_dict.FCStd', 'freecad')

   # Test exporting by directly assigning values to the shapes
   front_endcap.set_placement(placement=(0.08, 0.0, 0.0), local_origin=(0, 0.5, 0)).set_geometry(radius_m=0.22, thickness_m=0.08)
   center_pipe.set_placement(placement=(0.08, 0.0, 0.0), local_origin=(1, 0.5, 0)).set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)
   rear_endcap.set_placement(placement=(0.68, 0.0, 0.0), local_origin=(1, 0.5, 0)).set_geometry(radius_m=0.22, thickness_m=0.08)
   sphere.set_placement(placement=(1.0, 0.0, 0.22), local_origin=(0, 0.5, 0.5)).set_geometry(radius_m=0.2)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   assembly.make_concrete().export('assembly_no_attachment_direct.FCStd', 'freecad')

   # Clean up any newly created files
   if not retain_output:
      os.remove('assembly_no_attachment_dict.FCStd')
      os.remove('assembly_no_attachment_direct.FCStd')


def test_assembly_some_attachments(retain_output: bool):

   # Create assembly with some attachments
   assembly = Assembly('AssemblySomeAttachments')
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)
   center_pipe = Pipe('Center', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('FrontAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RearAttachment', x=0.5, y=0.0, z=1.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)
   sphere = Sphere('RandomSphere', 1000.0)
   center_pipe.attach('FrontAttachment', front_endcap, 'CenterAttachment')\
              .attach('RearAttachment', rear_endcap, 'CenterAttachment')

   # Test exporting using a symbolic lookup dictionary
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   concrete_params = {
      'FrontEndcap_origin_x': 0.0,
      'FrontEndcap_origin_y': 0.5,
      'FrontEndcap_origin_z': 0.0,
      'FrontEndcap_placement_x': 0.08,
      'FrontEndcap_placement_y': 0.0,
      'FrontEndcap_placement_z': 0.0,
      'FrontEndcap_radius': 0.22,
      'FrontEndcap_thickness': 0.08,
      'Center_radius': 0.22,
      'Center_height': 0.6,
      'Center_thickness': 0.0025,
      'RearEndcap_radius': 0.22,
      'RearEndcap_thickness': 0.08,
      'RandomSphere_origin_x': 0.0,
      'RandomSphere_origin_y': 0.5,
      'RandomSphere_origin_z': 0.5,
      'RandomSphere_placement_x': 1.0,
      'RandomSphere_placement_y': 0.0,
      'RandomSphere_placement_z': 0.22,
      'RandomSphere_radius': 0.2
   }
   assembly.make_concrete(concrete_params).export('assembly_some_attachments_dict.FCStd', 'freecad')

   # Test exporting by directly assigning values to the shapes
   front_endcap.set_geometry(radius_m=0.22, thickness_m=0.08)
   center_pipe.set_placement(placement=(0.08, 0.0, 0.0), local_origin=(1, 0.5, 0)).set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)
   rear_endcap.set_geometry(radius_m=0.22, thickness_m=0.08)
   sphere.set_placement(placement=(1.0, 0.0, 0.22), local_origin=(0, 0.5, 0.5)).set_geometry(radius_m=0.2)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   assembly.make_concrete().export('assembly_some_attachments_direct.FCStd', 'freecad')

   # Clean up any newly created files
   if not retain_output:
      os.remove('assembly_some_attachments_dict.FCStd')
      os.remove('assembly_some_attachments_direct.FCStd')


def test_assembly_all_attachments(retain_output: bool):

   # Create a fully attached assembly
   assembly = Assembly('AssemblyFullAttachments')
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)
   center_pipe = Pipe('Center', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('FrontAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RearAttachment', x=0.5, y=0.0, z=1.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RandomAttachment', x=0.5, y=0.5, z=1.0)
   sphere = Sphere('RandomSphere', 1000.0)\
      .add_attachment_point('Front', x=0.0, y=0.5, z=0.5)
   support = Cylinder('SupportStrut', 1000.0).set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('End1', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('End2', x=0.5, y=0.5, z=1.0)
   center_pipe.attach('FrontAttachment', front_endcap, 'CenterAttachment')\
              .attach('RearAttachment', rear_endcap, 'CenterAttachment')
   rear_endcap.attach('RandomAttachment', support, 'End1')
   sphere.attach('Front', support, 'End2')

   # Test exporting using a symbolic lookup dictionary
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   assembly.add_part(support)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   concrete_params = {
      'FrontEndcap_radius': 0.22,
      'FrontEndcap_thickness': 0.08,
      'Center_origin_x': 1.0,
      'Center_origin_y': 0.5,
      'Center_origin_z': 0.0,
      'Center_placement_x': 0.08,
      'Center_placement_y': 0.0,
      'Center_placement_z': 0.0,
      'Center_radius': 0.22,
      'Center_height': 0.6,
      'Center_thickness': 0.0025,
      'RearEndcap_radius': 0.22,
      'RearEndcap_thickness': 0.08,
      'RandomSphere_radius': 0.2,
      'SupportStrut_radius': 0.01,
      'SupportStrut_height': 0.24
   }
   assembly.make_concrete(concrete_params).export('assembly_full_attachments_dict.FCStd', 'freecad')

   # Test exporting by directly assigning values to the shapes
   center_pipe.set_placement(placement=(0.08, 0.0, 0.0), local_origin=(1, 0.5, 0)).set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)
   front_endcap.set_geometry(radius_m=0.22, thickness_m=0.08)
   rear_endcap.set_geometry(radius_m=0.22, thickness_m=0.08)
   sphere.set_geometry(radius_m=0.2)
   support.set_geometry(radius_m=0.01, height_m=0.24)
   if retain_output:
      print('\nFree Parameters: {}'.format(assembly.get_free_parameters()))
   assembly.make_concrete().export('assembly_full_attachments_direct.FCStd', 'freecad')

   # Clean up any newly created files
   if not retain_output:
      os.remove('assembly_full_attachments_dict.FCStd')
      os.remove('assembly_full_attachments_direct.FCStd')


def test_assembly_properties(retain_output: bool = False):

   # Create a set of random components
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.5, z=0.0)
   center_pipe = Pipe('Center', 1000.0)\
      .set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('FrontAttachment', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('RearAttachment', x=0.5, y=0.5, z=1.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('RandomAttachment', x=0.5, y=0.5, z=1.0)
   sphere = Sphere('RandomSphere', 1000.0)\
      .set_geometry(radius_m=0.2)\
      .add_attachment_point('Front', x=0.0, y=0.5, z=0.5)
   support = Cylinder('SupportStrut', 1000.0)\
      .set_geometry(radius_m=0.01, height_m=0.24)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('End1', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('End2', x=0.5, y=0.5, z=1.0)

   # Create a fully attached assembly
   assembly = Assembly('FullAssembly')
   center_pipe.attach('FrontAttachment', front_endcap, 'CenterAttachment')\
              .attach('RearAttachment', rear_endcap, 'CenterAttachment')
   rear_endcap.attach('RandomAttachment', support, 'End1')
   sphere.attach('Front', support, 'End2')
   center_pipe.set_placement(placement=(0.08, 0.0, 0.0),
                             local_origin=(1, 0.5, 0))
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   assembly.add_part(support)

   # Retrieve cumulative assembly properties from equations
   assembly.export('assembly.FCStd', 'freecad')
   if retain_output:
      print('\nProperties (Equation-Based):\n')
      print('\tMass: ', assembly.mass)
      print('\tMaterial Volume: ', assembly.material_volume)
      print('\tDisplaced Volume: ', assembly.displaced_volume)
      print('\tSurface Area: ', assembly.surface_area)
      print('\tCenter of Gravity: ', assembly.center_of_gravity)
      print('\tCenter of Buoyancy: ', assembly.center_of_buoyancy)
      # TODO: Length, width, and height
      #print('\tLength: ', assembly.length)
      #print('\tWidth: ', assembly.width)
      #print('\tHeight: ', assembly.height)

   # Retrieve cumulative assembly properties from CAD model
   properties = assembly.get_cad_physical_properties()
   if retain_output:
      print('\nProperties (CAD-Based):\n')
      print('\tMass: ', properties['mass'])
      print('\tMaterial Volume: ', properties['material_volume'])
      print('\tDisplaced Volume: ', properties['displaced_volume'])
      print('\tSurface Area: ', properties['surface_area'])
      print('\tCenter of Gravity: ({}, {}, {})'.format(properties['cg_x'], properties['cg_y'], properties['cg_z']))
      print('\tCenter of Buoyancy: ({}, {}, {})'.format(properties['cb_x'], properties['cb_y'], properties['cb_z']))
      # TODO: Length, width, and height
      #print('\tLength: ', properties['xlen'])
      #print('\tWidth: ', properties['ylen'])
      #print('\tHeight: ', properties['zlen'])

   # Verify that the equation- and CAD-based properties match
   assert abs(properties['mass'] - assembly.mass) < 5.0
   assert abs(properties['material_volume'] - assembly.material_volume) < 0.005
   assert abs(properties['displaced_volume'] - assembly.displaced_volume) < 0.005
   assert abs(properties['surface_area'] - assembly.surface_area)
   assert abs(properties['cg_x'] - assembly.center_of_gravity[0]) < 0.03
   assert abs(properties['cg_y'] - assembly.center_of_gravity[1]) < 0.001
   assert abs(properties['cg_z'] - assembly.center_of_gravity[2]) < 0.001
   assert abs(properties['cb_x'] - assembly.center_of_buoyancy[0]) < 0.01
   assert abs(properties['cb_y'] - assembly.center_of_buoyancy[1]) < 0.001
   assert abs(properties['cb_z'] - assembly.center_of_buoyancy[2]) < 0.001
   # TODO: Length, width, and height
   #assert abs(properties['length'] - assembly.length)
   #assert abs(properties['width'] - assembly.width)
   #assert abs(properties['height'] - assembly.height)

   # Clean up any newly created files
   if not retain_output:
      os.remove('assembly.FCStd')


if __name__ == '__main__':

   test_assembly_no_attachments(False)
   test_assembly_some_attachments(False)
   test_assembly_all_attachments(False)
   test_assembly_properties(False)
