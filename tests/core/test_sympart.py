#!/usr/bin/env python3

from symcad.parts import Box, FlangedFlatPlate
from symcad.core import SymPart
from sympy import Expr, Symbol
import math, os

if __name__ == '__main__':

   # Test direct abstract SymPart instance creation
   successful_failure = False
   try:
      SymPart('test', None)
   except TypeError:
      successful_failure = True
   assert successful_failure == True, f'Direct creation of a SymPart abstract object should have failed'

   # Test SymPart creation (using FlangedFlatPlate as a proxy)
   shape_id = 'test'
   shape = FlangedFlatPlate(shape_id)
   assert shape.name == shape_id
   assert len(shape.attachment_points) == 0
   assert len(shape.attachments) == 0
   assert len(shape.connection_ports) == 0
   assert len(shape.connections) == 0
   assert shape.static_center_of_placement == None
   assert shape.static_placement == None
   assert shape.orientation.name == shape_id + '_orientation'
   assert isinstance(shape.orientation.yaw, float)
   assert isinstance(shape.orientation.pitch, float)
   assert isinstance(shape.orientation.roll, float)
   assert shape.orientation.yaw == 0.0
   assert shape.orientation.pitch == 0.0
   assert shape.orientation.roll == 0.0
   assert shape.material_density == 1.0
   assert shape.is_exposed == True

   # Test adding attachment points
   shape.add_attachment_point('attachment_point1', x=1.0, y=2.0, z=3.0)
   shape.add_attachment_point('attachment_point2', x=3.0, y=2.0, z=1.0)
   assert len(shape.attachment_points) == 2
   assert shape.attachment_points[0].name == 'attachment_point1'
   assert isinstance(shape.attachment_points[0].x, float)
   assert isinstance(shape.attachment_points[0].y, float)
   assert isinstance(shape.attachment_points[0].z, float)
   assert shape.attachment_points[0].x == 1.0
   assert shape.attachment_points[0].y == 2.0
   assert shape.attachment_points[0].z == 3.0
   assert shape.attachment_points[1].name == 'attachment_point2'
   assert isinstance(shape.attachment_points[1].x, float)
   assert isinstance(shape.attachment_points[1].y, float)
   assert isinstance(shape.attachment_points[1].z, float)
   assert shape.attachment_points[1].x == 3.0
   assert shape.attachment_points[1].y == 2.0
   assert shape.attachment_points[1].z == 1.0

   # Test adding connection ports
   shape.add_connection_port('connection_port1', x=10.0, y=12.0, z=13.0)
   shape.add_connection_port('connection_port2', x=20.0, y=22.0, z=23.0)
   assert len(shape.connection_ports) == 2
   assert shape.connection_ports[0].name == 'connection_port1'
   assert isinstance(shape.connection_ports[0].x, float)
   assert isinstance(shape.connection_ports[0].y, float)
   assert isinstance(shape.connection_ports[0].z, float)
   assert shape.connection_ports[0].x == 10.0
   assert shape.connection_ports[0].y == 12.0
   assert shape.connection_ports[0].z == 13.0
   assert shape.connection_ports[1].name == 'connection_port2'
   assert isinstance(shape.connection_ports[1].x, float)
   assert isinstance(shape.connection_ports[1].y, float)
   assert isinstance(shape.connection_ports[1].z, float)
   assert shape.connection_ports[1].x == 20.0
   assert shape.connection_ports[1].y == 22.0
   assert shape.connection_ports[1].z == 23.0

   # Test built-in mathematical functionality
   shape.set_geometry(radius_m=1.0, thickness_m=3.0)
   shape *= 2.0
   assert shape.geometry.radius == 2.0
   assert shape.geometry.thickness == 6.0
   shape /= 2.0
   assert shape.geometry.radius == 1.0
   assert shape.geometry.thickness == 3.0

   # Test manipulating the placement, center of placement, and offset
   shape.set_placement(placement=(3.0, Symbol('manual_placement_y'), None),
                       local_origin=(Symbol('manual_x_symbol'), 1.0, 2.0))
   assert shape.static_center_of_placement.name == shape_id + '_origin'
   assert isinstance(shape.static_center_of_placement.x, Expr)
   assert isinstance(shape.static_center_of_placement.y, float)
   assert isinstance(shape.static_center_of_placement.z, float)
   assert shape.static_center_of_placement.x == Symbol('manual_x_symbol')
   assert shape.static_center_of_placement.y == 1.0
   assert shape.static_center_of_placement.z == 2.0
   assert shape.static_placement.name == shape_id + '_placement'
   assert isinstance(shape.static_placement.x, float)
   assert isinstance(shape.static_placement.y, Expr)
   assert isinstance(shape.static_placement.z, Expr)
   assert shape.static_placement.x == 3.0
   assert shape.static_placement.y == Symbol('manual_placement_y')
   assert shape.static_placement.z == Symbol(shape_id + '_placement_z')

   # Test manipulating the orientation and exposure
   shape.set_orientation(roll_deg=45.0, pitch_deg=10.0, yaw_deg=Symbol('manual_yaw'))
   assert isinstance(shape.orientation.roll, float)
   assert isinstance(shape.orientation.pitch, float)
   assert isinstance(shape.orientation.yaw, Expr)
   assert shape.orientation.roll == math.radians(45.0)
   assert shape.orientation.pitch == math.radians(10.0)
   assert shape.orientation.yaw == Symbol('manual_yaw') * math.pi / 180.0
   shape.set_orientation(roll_deg=0.0, pitch_deg=0.0, yaw_deg=0.0)
   assert isinstance(shape.orientation.roll, float)
   assert isinstance(shape.orientation.pitch, float)
   assert isinstance(shape.orientation.yaw, float)
   assert shape.orientation.roll == 0.0
   assert shape.orientation.pitch == 0.0
   assert shape.orientation.yaw == 0.0
   assert shape.is_exposed == True
   shape.set_unexposed()
   assert shape.is_exposed == False

   # Test adding attachments and connections
   successful_failure = False
   shape1 = FlangedFlatPlate(shape_id)
   shape1.add_attachment_point('attachment_point1', x=1.0, y=2.0, z=3.0)
   shape1.add_attachment_point('attachment_point2', x=3.0, y=2.0, z=1.0)
   shape1.add_connection_port('connection_port1', x=10.0, y=12.0, z=13.0)
   shape1.add_connection_port('connection_port2', x=20.0, y=22.0, z=23.0)
   shape2 = FlangedFlatPlate(shape_id + '2')
   shape2.add_attachment_point('attachment_point1', x=1.0, y=2.0, z=3.0)
   shape2.add_attachment_point('attachment_point2', x=3.0, y=2.0, z=1.0)
   shape2.add_attachment_point('attachment_point4', x=0.0, y=0.0, z=1.0)
   shape2.add_connection_port('connection_port1', x=10.0, y=12.0, z=13.0)
   shape2.add_connection_port('connection_port2', x=20.0, y=22.0, z=23.0)
   shape2.add_connection_port('connection_port3', x=1.0, y=0.5, z=0.25)
   try:
      shape1.attach('attachment_point_1', shape2, 'attachment_point2')
   except ValueError:
      successful_failure = True
   assert successful_failure == True, f'Attachment of non-existent local attachment point should have failed'
   shape1.attach('attachment_point1', shape2, 'attachment_point2')
   shape1.attach('attachment_point2', shape2, 'attachment_point4')
   assert 'attachment_point1' in shape1.attachments
   assert 'attachment_point2' in shape1.attachments
   assert 'attachment_point3' not in shape1.attachments
   assert shape1.attachments['attachment_point1'] == shape2.name + '#attachment_point2'
   assert shape1.attachments['attachment_point2'] == shape2.name + '#attachment_point4'
   assert shape2.attachments['attachment_point2'] == shape1.name + '#attachment_point1'
   assert shape2.attachments['attachment_point4'] == shape1.name + '#attachment_point2'
   successful_failure = False
   try:
      shape1.connect('connection_port1', shape2, 'connection_port_1')
   except ValueError:
      successful_failure = True
   assert successful_failure == True, f'Connection of non-existent remote connection port should have failed'
   shape1.connect('connection_port1', shape2, 'connection_port1')
   shape1.connect('connection_port2', shape2, 'connection_port3')
   assert 'connection_port1' in shape1.connections
   assert 'connection_port2' in shape1.connections
   assert 'connection_port3' not in shape1.connections
   assert shape1.connections['connection_port1'] == shape2.name + '#connection_port1'
   assert shape1.connections['connection_port2'] == shape2.name + '#connection_port3'
   assert shape2.connections['connection_port1'] == shape1.name + '#connection_port1'
   assert shape2.connections['connection_port3'] == shape1.name + '#connection_port2'

   # Test exporting as a CAD model
   assert shape1.__cad__ is not None
   shape.set_geometry(radius_m=1.0, thickness_m=0.01)
   shape.export('test_output.FCStd', 'freecad')
   shape.export('test_output.stl', 'stl')
   shape.export('test_output.stp', 'step')
   os.remove('test_output.FCStd')
   os.remove('test_output.stl')
   os.remove('test_output.stp')

   # Test cloning a SymPart
   cloned_shape = shape.clone()
   assert cloned_shape == shape

   # Test retrieving CAD-based physical properties
   props = shape.get_cad_physical_properties()
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'min_x' in props and 'min_y' in props and 'min_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['cb_x'], float) and isinstance(props['cb_y'], float) and isinstance(props['cb_z'], float)
   assert isinstance(props['min_x'], float) and isinstance(props['min_y'], float) and isinstance(props['min_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['surface_area'], float) and isinstance(props['mass'], float)

   # Test physical properties after part rotation
   shape = Box('test_box', 1000.0)\
      .set_geometry(length_m=4.0, width_m=2.5, height_m=2.0, thickness_m=0.01)\
      .set_orientation(roll_deg=45.0, pitch_deg=-10.0, yaw_deg=30.0)\
      .set_placement(placement=(0.0, 0.0, 0.0), local_origin=(0.0, 0.0, 0.0))
   props = shape.get_cad_physical_properties()
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'min_x' in props and 'min_y' in props and 'min_z' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props and 'mass' in props
   assert 'material_volume' in props and 'displaced_volume' in props and 'surface_area' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['cb_x'], float) and isinstance(props['cb_y'], float) and isinstance(props['cb_z'], float)
   assert isinstance(props['min_x'], float) and isinstance(props['min_y'], float) and isinstance(props['min_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['surface_area'], float) and isinstance(props['mass'], float)
   assert abs(shape.oriented_length - props['xlen']) < 0.001
   assert abs(shape.oriented_width - props['ylen']) < 0.001
   assert abs(shape.oriented_height - props['zlen']) < 0.001
   assert abs(shape.material_volume - props['material_volume']) < 0.001
   assert abs(shape.displaced_volume - props['displaced_volume']) < 0.001
   assert abs(shape.surface_area - props['surface_area']) < 0.001
   assert abs(shape.mass - props['mass']) < 0.001
