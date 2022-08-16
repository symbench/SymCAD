#!/usr/bin/env python3

from symcad.core import Assembly
from symcad.parts import Cylinder, FlangedFlatPlate, Pipe, Sphere

def symbolic_assembly():

   # Create random symbolic components
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)
   center_pipe = Pipe('Center', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   sphere = Sphere('RandomSphere', 1000.0)
   support = Cylinder('SupportStrut', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)

   # Create Assembly-by-Placement
   assembly = Assembly('AssemblyNoAttachments')
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   assembly.add_part(support)

   # Export CAD model using dictionary of parameter values
   concrete_params = {
      'FrontEndcap_origin_x': 0.5,
      'FrontEndcap_origin_y': 0.5,
      'FrontEndcap_origin_z': 1.0,
      'FrontEndcap_placement_x': 0.0,
      'FrontEndcap_placement_y': 0.0,
      'FrontEndcap_placement_z': 0.0,
      'FrontEndcap_radius': 0.22,
      'FrontEndcap_thickness': 0.08,
      'Center_origin_x': 0.5,
      'Center_origin_y': 0.5,
      'Center_origin_z': 0.0,
      'Center_placement_x': 0.08,
      'Center_placement_y': 0.0,
      'Center_placement_z': 0.0,
      'Center_radius': 0.22,
      'Center_height': 0.6,
      'Center_thickness': 0.0025,
      'RearEndcap_origin_x': 0.5,
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
      'RandomSphere_placement_z': 0.0,
      'RandomSphere_radius': 0.2,
      'SupportStrut_origin_x': 0.5,
      'SupportStrut_origin_y': 0.5,
      'SupportStrut_origin_z': 0.0,
      'SupportStrut_placement_x': 0.76,
      'SupportStrut_placement_y': 0.0,
      'SupportStrut_placement_z': 0.0,
      'SupportStrut_radius': 0.01,
      'SupportStrut_height': 0.24
   }
   assembly.make_concrete(concrete_params)\
           .export('assembly_by_placement_symbolic.FCStd', 'freecad')


def concrete_assembly():

   # Create random concrete components
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)
   center_pipe = Pipe('Center', 1000.0)\
      .set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)
   sphere = Sphere('RandomSphere', 1000.0)\
      .set_geometry(radius_m=0.2)
   support = Cylinder('SupportStrut', 1000.0)\
      .set_geometry(radius_m=0.01, height_m=0.24)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)

   # Create Assembly-by-Placement
   assembly = Assembly('AssemblyNoAttachments')
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   assembly.add_part(support)

   # Manually place all components and export the CAD assembly
   front_endcap.set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.5, 0.5, 1.0))
   center_pipe.set_placement(placement=(0.08, 0.0, 0.0), local_origin=(0.5, 0.5, 0.0))
   rear_endcap.set_placement(placement=(0.68, 0.0, 0.0), local_origin=(0.5, 0.5, 0.0))
   sphere.set_placement(placement=(1.0, 0.0, 0.0), local_origin=(0.0, 0.5, 0.5))
   support.set_placement(placement=(0.76, 0.0, 0.0), local_origin=(0.5, 0.5, 0.0))
   assembly.export('assembly_by_placement_concrete.FCStd', 'freecad')


if __name__ == '__main__':

   concrete_assembly()
   symbolic_assembly()
