#!/usr/bin/env python3

from symcad.core import Assembly, GraphAPI
from symcad.parts import Capsule
import json, os

if __name__ == '__main__':

   # Create a test assembly
   assembly = Assembly('TestAssembly')
   test_capsule1 = Capsule('test_capsule1', 900.0)\
      .set_orientation(roll_deg=0, pitch_deg=-90, yaw_deg=0)\
      .add_attachment_point('FrontCenter', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('RearCenter', x=0.5, y=0.5, z=1.0)\
      .add_attachment_point('MiddleBottom', x=1.0, y=0.5, z=0.5)\
      .add_attachment_point('MiddleTop', x=0.0, y=0.5, z=0.5)\
      .add_connection_port('ElectricalPort1', x=0.0, y=0.5, z=0.75)\
      .add_connection_port('ElectricalPort2', x=1.0, y=0.5, z=0.75)\
      .set_placement(placement=(None, 0.0, None), local_origin=(0, 0, 0))
   test_capsule2 = Capsule('test_capsule2', 1000.0)\
      .set_orientation(roll_deg=None, pitch_deg=-90, yaw_deg=None).set_unexposed()\
      .set_geometry(cylinder_length_m=1.0, cylinder_radius_m=0.6, endcap_length_m=0.3, thickness_m=0.01)\
      .add_attachment_point('FrontCenter', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('RearCenter', x=0.5, y=0.5, z=1.0)\
      .add_attachment_point('MiddleBottom', x=1.0, y=0.5, z=0.5)\
      .add_attachment_point('MiddleTop', x=0.0, y=0.5, z=0.5)\
      .add_connection_port('ElectricalPort1', x=0.0, y=0.5, z=0.75)\
      .add_connection_port('ElectricalPort2', x=1.0, y=0.5, z=0.75)
   test_capsule3 = Capsule('test_capsule3', 1100.0)\
      .set_orientation(roll_deg=0, pitch_deg=90, yaw_deg=0)\
      .add_attachment_point('FrontCenter', x=0.5, y=0.5, z=1.0)\
      .add_attachment_point('RearCenter', x=0.5, y=0.5, z=0.0)\
      .add_attachment_point('MiddleBottom', x=0.0, y=0.5, z=0.5)\
      .add_attachment_point('MiddleTop', x=1.0, y=0.5, z=0.5)\
      .add_connection_port('ElectricalPort1', x=1.0, y=0.5, z=0.25)\
      .add_connection_port('ElectricalPort2', x=0.0, y=0.5, z=0.25)
   test_capsule2.attach('FrontCenter', test_capsule1, 'RearCenter')
   test_capsule3.attach('MiddleTop', test_capsule2, 'MiddleBottom')
   test_capsule1.connect('ElectricalPort1', test_capsule2, 'ElectricalPort1')
   test_capsule1.connect('ElectricalPort2', test_capsule3, 'ElectricalPort2')
   assembly.add_part(test_capsule1)
   assembly.add_part(test_capsule2)
   assembly.add_part(test_capsule3)

   # Test exporting to a JSON string
   json_out = GraphAPI.export_to_json(assembly)
   with open(os.path.realpath(os.path.dirname(__file__)) + '/test_json_graph.json', 'r') as file:
      reference_json_out = file.read()
   assert json.loads(json_out) == json.loads(reference_json_out)

   # Test reimporting back into SymCAD
   assembly_in = GraphAPI.import_from_json(json_out)
   assert assembly_in == assembly

   # Verify that exporting the reimported model matches the reference export
   json_out2 = GraphAPI.export_to_json(assembly_in)
   assert json.loads(json_out2) == json.loads(reference_json_out)

   # Test exporting and loading directly from the assembly to a file
   file_name = 'test_assembly_save.json'
   assembly.save(file_name)
   assembly_in = Assembly.load(file_name)
   assert assembly_in == assembly
   os.remove(file_name)
