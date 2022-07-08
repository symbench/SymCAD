#!/usr/bin/env python3
# Copyright (C) 2022, Will Hedgecock
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The GraphAPI module provides methods and functionality for interacting with the graph-based
data representation of a `symcad.core.Assembly` in the SymCAD library.

All methods within this module are for internal use only and should not be directly accessed
by any external module. Interacting with graph-based `Assembly` representations should be
done via the `symcad.core.Assembly.Assembly.save()` and `symcad.core.Assembly.Assembly.load()`
methods.

The SymCAD Graph Schema for an `Assembly` is JSON-based, as follows:

```python
{
   "name": str,
   "parts": [
      {
         "name": str,
         "type": str,
         "geometry": {
            "property1": str | float,
         },
         "material_density": float,
         "static_origin": null | {
            "x": str | float,
            "y": str | float,
            "z": str | float
         },
         "static_placement": null | {
            "x": str | float,
            "y": str | float,
            "z": str | float
         },
         "attachment_points": [
            {
               "name": str,
               "x": float,
               "y": float,
               "z": float
            }
         ],
         "connection_ports": [
            {
               "name": str,
               "x": float,
               "y": float,
               "z": float
            }
         ],
         "orientation": {
            "roll": str | float,
            "pitch": str | float,
            "yaw": str | float
         },
         "is_exposed": true | false
      }
   ],
   "attachments": [
      {
         "source_node": str,
         "source_attachment": str,
         "destination_node": str,
         "destination_attachment": str
      }
   ],
   "connections": [
      {
         "source_node": str,
         "source_connection": str,
         "destination_node": str,
         "destination_connection": str
      }
   ]
}
```
"""

from __future__ import annotations
from .Coordinate import Coordinate
from .Geometry import Geometry
from .Assembly import Assembly
from typing import Any
import json, math, sympy


def _isfloat(num: Any) -> bool:
   """Private helper function to test if a value is float-convertible."""
   try:
      float(num)
      return True
   except TypeError:
      return False


def export_to_json(assembly: Assembly) -> str:
   """Returns a string-based JSON representation of the specified `Assembly`."""

   # Iterate through all SymCAD parts in the assembly
   json_dict = { 'name': assembly.name, 'parts': [], 'attachments': [], 'connections': [] }
   for part in assembly.parts:

      # Create static origin and placement structures
      if part.static_origin is not None:
         static_origin = {
            'x': str(part.static_origin.x)
                    if not _isfloat(part.static_origin.x) else
                 float(part.static_origin.x),
            'y': str(part.static_origin.y)
                    if not _isfloat(part.static_origin.y) else
                 float(part.static_origin.y),
            'z': str(part.static_origin.z)
                    if not _isfloat(part.static_origin.z) else
                 float(part.static_origin.z)
         }
      else:
         static_origin = None
      if part.static_placement is not None:
         static_placement = {
            'x': str(part.static_placement.x)
                    if not _isfloat(part.static_placement.x) else
                 float(part.static_placement.x),
            'y': str(part.static_placement.y)
                    if not _isfloat(part.static_placement.y) else
                 float(part.static_placement.y),
            'z': str(part.static_placement.z)
                    if not _isfloat(part.static_placement.z) else
                 float(part.static_placement.z)
         }
      else:
         static_placement = None

      # Create a JSON structure for the current part
      component = {
         'name': part.name,
         'type': '.'.join(str(part.__class__).split('\'')[1].split('.')[2:-1]),
         'geometry': {k: str(part.geometry.__dict__[k])
                             if not _isfloat(part.geometry.__dict__[k]) else
                          part.geometry.__dict__[k]
                      for k in set(list(part.geometry.__dict__.keys())) - {'name'}},
         'material_density': part.material_density,
         'static_origin': static_origin,
         'static_placement': static_placement,
         'attachment_points': [pt.__dict__ for pt in part.attachment_points],
         'connection_ports': [pt.__dict__ for pt in part.connection_ports],
         'orientation': {
            'roll': str(part.orientation.roll)
                       if not _isfloat(part.orientation.roll) else
                    math.degrees(part.orientation.roll),
            'pitch': str(part.orientation.pitch)
                        if not _isfloat(part.orientation.pitch) else
                     math.degrees(part.orientation.pitch),
            'yaw': str(part.orientation.yaw)
                      if not _isfloat(part.orientation.yaw) else
                   math.degrees(part.orientation.yaw)
         },
         'is_exposed': part.is_exposed
      }

      # Create an attachment structure for each attachment in the current part
      attachments = []
      for local_attachment, remote_attachment in part.attachments.items():
         attachments.append({
            'source_node': part.name,
            'source_attachment': local_attachment,
            'destination_node': remote_attachment.split('#')[0],
            'destination_attachment': remote_attachment.split('#')[1]
         })

      # Create a connection structure for each connection in the current part
      connections = []
      for local_connection, remote_connection in part.connections.items():
         connections.append({
            'source_node': part.name,
            'source_connection': local_connection,
            'destination_node': remote_connection.split('#')[0],
            'destination_connection': remote_connection.split('#')[1]
         })

      # Append the part component and its attachments to the JSON structure
      json_dict['parts'].append(component)
      for new_attach in attachments:
         already_exists = False
         for attach2 in json_dict['attachments']:
            if new_attach['source_node'] == attach2['destination_node'] and \
                  new_attach['source_attachment'] == attach2['destination_attachment'] and \
                  new_attach['destination_node'] == attach2['source_node'] and \
                  new_attach['destination_attachment'] == attach2['source_attachment']:
               already_exists = True
         if not already_exists:
            json_dict['attachments'].append(new_attach)

      # Append the part connections to the JSON structure
      for new_connect in connections:
         already_exists = False
         for connect2 in json_dict['connections']:
            if new_connect['source_node'] == connect2['destination_node'] and \
                  new_connect['source_connection'] == connect2['destination_connection'] and \
                  new_connect['destination_node'] == connect2['source_node'] and \
                  new_connect['destination_connection'] == connect2['source_connection']:
               already_exists = True
         if not already_exists:
            json_dict['connections'].append(new_connect)

   # Return a string representation of the complete JSON structure
   return json.dumps(json_dict, indent=3)


def import_from_json(json_str: str) -> Assembly:
   """Returns a new `Assembly` parsed from its JSON string representation in `json_str`."""

   # Parse the JSON string as an actual JSON dictionary
   json_dict = json.loads(json_str)
   assembly = Assembly(json_dict['name'])

   # Iterate through all parts in the JSON structure
   for part in json_dict['parts']:

      # Convert the JSON part into its SymCAD representation
      part_class = getattr(__import__('symcad'), 'parts')
      for comp in part['type'].split('.'):
         part_class = getattr(part_class, comp)
      shape = part_class(part['name'])
      geometry = Geometry(part['name'])
      for property, value in part['geometry'].items():
         setattr(geometry, property, sympy.Symbol(value) if isinstance(value, str) else value)
      setattr(shape, 'geometry', geometry)
      setattr(shape, 'material_density', part['material_density'])
      if part['static_origin'] is not None:
         setattr(shape, 'static_origin',
            Coordinate(part['name'] + '_origin',
                       x=sympy.Symbol(part['static_origin']['x'])
                            if isinstance(part['static_origin']['x'], str) else
                         part['static_origin']['x'],
                       y=sympy.Symbol(part['static_origin']['y'])
                            if isinstance(part['static_origin']['y'], str) else
                         part['static_origin']['y'],
                       z=sympy.Symbol(part['static_origin']['z'])
                            if isinstance(part['static_origin']['z'], str) else
                         part['static_origin']['z']))
      if part['static_placement'] is not None:
         setattr(shape, 'static_placement',
            Coordinate(part['name'] + '_placement',
                       x=sympy.Symbol(part['static_placement']['x'])
                            if isinstance(part['static_placement']['x'], str) else
                         part['static_placement']['x'],
                       y=sympy.Symbol(part['static_placement']['y'])
                            if isinstance(part['static_placement']['y'], str) else
                         part['static_placement']['y'],
                       z=sympy.Symbol(part['static_placement']['z'])
                            if isinstance(part['static_placement']['z'], str) else
                         part['static_placement']['z']))
      attachment_points = []
      for attachment_point in part['attachment_points']:
         attachment_points.append(Coordinate(attachment_point['name'],
                                             x=attachment_point['x'],
                                             y=attachment_point['y'],
                                             z=attachment_point['z']))
      connection_ports = []
      for connection_port in part['connection_ports']:
         connection_ports.append(Coordinate(connection_port['name'],
                                            x=connection_port['x'],
                                            y=connection_port['y'],
                                            z=connection_port['z']))
      setattr(shape, 'attachment_points', attachment_points)
      setattr(shape, 'connection_ports', connection_ports)
      setattr(getattr(shape, 'orientation'), 'roll',
              sympy.Symbol(part['orientation']['roll'])
                 if isinstance(part['orientation']['roll'], str) else
               math.radians(part['orientation']['roll']))
      setattr(getattr(shape, 'orientation'), 'pitch',
              sympy.Symbol(part['orientation']['pitch'])
                 if isinstance(part['orientation']['pitch'], str) else
               math.radians(part['orientation']['pitch']))
      setattr(getattr(shape, 'orientation'), 'yaw',
              sympy.Symbol(part['orientation']['yaw'])
                 if isinstance(part['orientation']['yaw'], str) else
               math.radians(part['orientation']['yaw']))
      setattr(shape, 'is_exposed', part['is_exposed'])
      assembly.add_part(shape)

   # Make all necessary part attachments
   for attachment in json_dict['attachments']:
      for part in assembly.parts:
         if part.name == attachment['source_node']:
            source = part
         elif part.name == attachment['destination_node']:
            dest = part
      source.attach(attachment['source_attachment'], dest, attachment['destination_attachment'])

   # Make all necessary part connections
   for connection in json_dict['connections']:
      for part in assembly.parts:
         if part.name == connection['source_node']:
            source = part
         elif part.name == connection['destination_node']:
            dest = part
      source.connect(connection['source_connection'], dest, connection['destination_connection'])

   return assembly
