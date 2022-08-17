#!/usr/bin/env python3

from symcad.core import Assembly
from symcad.parts import Cylinder, FlangedFlatPlate, Pipe, Sphere

def symbolic_assembly_by_attachment():

   # Create random symbolic components
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)
   center_pipe = Pipe('Center', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('FrontAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RearAttachment', x=0.5, y=0.0, z=1.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RandomAttachment', x=0.5, y=0.5, z=1.0)
   sphere = Sphere('RandomSphere', 1000.0)\
      .add_attachment_point('Front', x=0.0, y=0.5, z=0.5)
   support = Cylinder('SupportStrut', 1000.0)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('End1', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('End2', x=0.5, y=0.5, z=1.0)

   # Create Assembly-by-Attachment
   assembly = Assembly('AssemblyWithAttachments')
   center_pipe.attach('FrontAttachment', front_endcap, 'CenterAttachment')\
              .attach('RearAttachment', rear_endcap, 'CenterAttachment')
   rear_endcap.attach('RandomAttachment', support, 'End1')
   sphere.attach('Front', support, 'End2')
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
      'FrontEndcap_placement_x': 0,
      'FrontEndcap_placement_y': 0,
      'FrontEndcap_placement_z': 0,
      'FrontEndcap_radius': 0.22,
      'FrontEndcap_thickness': 0.08,
      'Center_radius': 0.22,
      'Center_height': 0.6,
      'Center_thickness': 0.0025,
      'RearEndcap_radius': 0.22,
      'RearEndcap_thickness': 0.08,
      'RandomSphere_radius': 0.2,
      'SupportStrut_radius': 0.01,
      'SupportStrut_height': 0.24
   }
   assembly.make_concrete(concrete_params)\
           .export('assembly_by_attachment_symbolic.FCStd', 'freecad')


def concrete_assembly_by_attachment():

   # Create random concrete components
   front_endcap = FlangedFlatPlate('FrontEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=-90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)
   center_pipe = Pipe('Center', 1000.0)\
      .set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('FrontAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RearAttachment', x=0.5, y=0.0, z=1.0)
   rear_endcap = FlangedFlatPlate('RearEndcap', 1000.0)\
      .set_geometry(radius_m=0.22, thickness_m=0.08)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('CenterAttachment', x=0.5, y=0.0, z=0.0)\
      .add_attachment_point('RandomAttachment', x=0.5, y=0.5, z=1.0)
   sphere = Sphere('RandomSphere', 1000.0)\
      .set_geometry(radius_m=0.2)\
      .add_attachment_point('Front', x=0.0, y=0.5, z=0.5)
   support = Cylinder('SupportStrut', 1000.0)\
      .set_geometry(radius_m=0.01, height_m=0.24)\
      .set_orientation(roll_deg=0.0, pitch_deg=90.0, yaw_deg=0.0)\
      .add_attachment_point('End1', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('End2', x=0.5, y=0.5, z=1.0)

   # Create Assembly-by-Attachment
   assembly = Assembly('AssemblyWithAttachments')
   center_pipe.attach('FrontAttachment', front_endcap, 'CenterAttachment')\
              .attach('RearAttachment', rear_endcap, 'CenterAttachment')
   rear_endcap.attach('RandomAttachment', support, 'End1')
   sphere.attach('Front', support, 'End2')
   assembly.add_part(front_endcap)
   assembly.add_part(center_pipe)
   assembly.add_part(rear_endcap)
   assembly.add_part(sphere)
   assembly.add_part(support)

   # Globally placed the front endcap and export the CAD assembly
   front_endcap.set_placement(placement=(0, 0, 0), local_origin=(0.5, 0.5, 1))
   assembly.export('assembly_by_attachment_concrete.FCStd', 'freecad')


if __name__ == '__main__':

   concrete_assembly_by_attachment()
   symbolic_assembly_by_attachment()
