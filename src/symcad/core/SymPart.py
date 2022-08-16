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

from __future__ import annotations
from .ML import NeuralNet
from .CAD import ModeledCad, ScriptedCad
from .Coordinate import Coordinate
from .Geometry import Geometry
from .Rotation import Rotation
from typing import Callable, Dict, List, Literal
from typing import Optional, Tuple, TypeVar, Union
from copy import deepcopy
from sympy import Expr
import abc

SymPartSub = TypeVar('SymPartSub', bound='SymPart')

class SymPart(metaclass=abc.ABCMeta):
   """Symbolic part base class from which all SymParts inherit.

   Defines the interface to a set of abstract properties that all SymParts possess, including
   mass, material volume, displaced volume, surface area, centroid, centers of gravity and
   buouyancy, length, width, and height, among others. These properties may be concrete or
   symbolic, and they represent the external interface that is expected to be used when
   accessing the physical properties of a given SymPart.

   When creating a new SymPart, its geometry and global placement will be treated as symbolic
   parameters, and its global orientation will be assumed to be 0 such that the SymPart does not
   rotate in space. These assumptions can be overridden using the various `set_*` methods of the
   SymPart object. Attachment points can be defined to indicate areas on a SymPart that are able
   to rigidly attach to other SymParts, or connection ports can be defined to indicate areas that
   are able to flexibly and/or non-mechanically connect to other SymParts.

   By default, a SymPart is assumed to be environmentally exposed and thus contribute to such
   geometric properties as the displaced volume. If a SymPart is not exposed, for example a dry
   component inside of a pressurized container, this should be specified by calling the
   `set_unexposed()` method on the SymPart object.

   The local coordinate space of a SymPart is defined with its origin at the front, center,
   bottom of the part, where the x-axis extends positively from its front to its rear, the y-axis
   extends positively from the xz-plane to the right of the part when looking from the positive
   x-axis toward origin, and the z-axis extends positively from the bottom to the top of the part.
   """


   # Public attributes ----------------------------------------------------------------------------

   name: str
   """Unique, identifying name of the `SymPart` instance."""

   geometry: Geometry
   """Part-specific geometry parameters."""

   attachment_points: List[Coordinate]
   """List of local points on the SymPart that can attach to other SymParts."""

   attachments: Dict[str, str]
   """Dictionary of SymParts and attachment points that are rigidly attached to this SymPart."""

   connection_ports: List[Coordinate]
   """List of local points on the SymPart that can connect flexibly to other SymParts."""

   connections: Dict[str, str]
   """Dictionary of SymParts and connection ports that are flexibly connected to this SymPart."""

   static_origin: Union[Coordinate, None]
   """Local point on the unoriented SymPart that is used for static placement and rotation."""

   static_placement: Union[Coordinate, None]
   """Global static placement of the `static_origin` of the SymPart."""

   orientation: Rotation
   """Global orientation of the SymPart (no rotation by default)."""

   material_density: float
   """Uniform material density in `kg/m^3` to be used in mass property calculations."""

   current_states: List[str]
   """List of geometric states for which the SymPart is currently configured."""

   is_exposed: bool
   """Whether the SymPart is environmentally exposed versus contained in another element."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str,
                      cad_representation: Union[str, Callable],
                      properties_model: Union[str, NeuralNet, None],
                      material_density: float) -> None:
      """Initializes an instance of a `SymPart`.

      The underlying `cad_representation` may either be a predefined FreeCAD model or a reference
      to a method that is able to create such a model. The `material_density` indicates the
      uniform material density in `kg/m^3` that should be used in mass property calculations for
      the given SymPart.

      Parameters
      ----------
      identifier : `str`
         Unique, identifying name for the SymPart.
      cad_representation : `Union[str, Callable]`
         Either the path to a representative CAD model for the given SymPart or a callable method
         that can create such a model.
      properties_model : `Union[str, NeuralNet, None]`
         Path to or instance of a neural network that may be evaluated to obtain the underlying
         geometric properties for the given SymPart.
      material_density: `float`
         Uniform material density in `kg/m^3` to be used in mass property calculations.
      """
      super().__init__()
      self.name = identifier
      self.geometry = Geometry(identifier)
      self.attachment_points = []
      self.attachments = {}
      self.connection_ports = []
      self.connections = {}
      self.static_origin = None
      self.static_placement = None
      self.orientation = Rotation(identifier + '_orientation')
      self.material_density = material_density
      self.current_states = []
      self.is_exposed = True
      self.__cad__ = ModeledCad(cad_representation) if isinstance(cad_representation, str) else \
                     ScriptedCad(cad_representation)
      self.__neural_net__ = NeuralNet(identifier, properties_model) \
                               if (properties_model and isinstance(properties_model, str)) else \
                            properties_model


   # Built-in method implementations --------------------------------------------------------------

   def __repr__(self) -> str:
      return str(type(self)).split('.')[-1].split('\'')[0] + ' (' + self.name + '): Geometry: [' \
             + str(self.geometry) + '], Placement: [' + str(self.static_placement) \
             + '], Orientation: [' + str(self.orientation) + '], Density: ' \
             + str(self.material_density) + ' kg/m^3, Exposed: ' + str(self.is_exposed)

   def __eq__(self, other: SymPart) -> bool:
      for key, val in self.__dict__.items():
         if key != 'name' and (key not in other.__dict__ or val != getattr(other, key)):
            return False
      return type(self) == type(other)

   def __copy__(self):
      copy = self.__class__.__new__(self.__class__)
      copy.__dict__.update(self.__dict__)
      return copy

   def __deepcopy__(self, memo):
      copy = self.__class__.__new__(self.__class__)
      memo[id(self)] = copy
      for key, val in self.__dict__.items():
         setattr(copy, key, deepcopy(val, memo))
      return copy

   def __imul__(self: SymPartSub, value: float) -> SymPartSub:
      self.geometry *= value
      return self

   def __itruediv__(self: SymPartSub, value: float) -> SymPartSub:
      self.geometry /= value
      return self


   # Public methods -------------------------------------------------------------------------------

   def clone(self: SymPartSub) -> SymPartSub:
      """Returns an exact clone of this `SymPart` instance."""
      return deepcopy(self)


   def set_placement(self: SymPartSub, *, placement: Tuple[Union[float, Expr, None],
                                                           Union[float, Expr, None],
                                                           Union[float, Expr, None]],
                                          local_origin: Tuple[float, float, float]) -> SymPartSub:
      """Sets the global placement of the `local_origin` of this SymPart.

      Parameters
      ----------
      placement : `Tuple` of `Union[float, sympy.Expr, None]`
         Global XYZ placement of the `local_origin` of the SymPart in meters. If `None` is
         specified for any given axis, placement on that axis will be treated as a symbol.
      local_origin : `Tuple[float, float, float]`
         Local XYZ point on the unoriented SymPart to be used for static placement and rotation.
         Each coordinate of the origin point should fall in the range `[0.0, 1.0]` and be relative
         to the *x-axis* length, *y-axis* width, and *z-axis* height of the SymPart with its
         origin at the front, left, center of the part.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      if self.static_placement is None:
         self.static_placement = Coordinate(self.name + '_placement')
      self.static_placement.set(x=placement[0], y=placement[1], z=placement[2])
      if self.static_origin is None:
         self.static_origin = Coordinate(self.name + '_origin')
      self.static_origin.set(x=local_origin[0], y=local_origin[1], z=local_origin[2])
      return self


   def set_orientation(self: SymPartSub, *, roll_deg: Union[float, Expr, None],
                                            pitch_deg: Union[float, Expr, None],
                                            yaw_deg: Union[float, Expr, None]) -> SymPartSub:
      """Sets the global orientation of the SymPart when rotated about its `z-`, `y-`, then
      `x-axis` (`yaw`, `pitch`, then `roll`) using a right-hand coordinate system.

      A positive `roll_deg` will tilt the part to the left from the point of view of a location
      inside the part. A positive `pitch_deg` will rotate the nose of the part downward, and a
      positive `yaw_deg` will rotate the nose of the part toward the left from the point of view
      of a location inside the part.

      Parameters
      ----------
      roll_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic roll angle in degrees. If `None` is specified, the angle will be
         treated as a symbol.
      pitch_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic pitch angle in degrees. If `None` is specified, the angle will be
         treated as a symbol.
      yaw_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic yaw angle in degress. If `None` is specified, the angle will be
         treated as a symbol.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      self.orientation.set(roll_deg=roll_deg, pitch_deg=pitch_deg, yaw_deg=yaw_deg)
      return self


   def set_state(self: SymPartSub, state_names: Union[List[str], None]) -> SymPartSub:
      """Sets the geometric configuration of the SymPart according to the indicated `state_names`.

      The concrete, overriding `SymPart` class may use these `state_names` to alter its underlying
      geometric properties.

      Parameters
      ----------
      state_names : `Union[List[str], None]`
         List of geometric states for which the part should be configured. If set to `None`,
         the part will be configured in its default state.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      self.current_states = [] if not state_names else \
                            [state for state in state_names if state in self.get_valid_states()]
      return self


   def set_unexposed(self: SymPartSub) -> SymPartSub:
      """Specifies that the SymPart is environmentally unexposed.

      This results in the part being excluded from certain geometric property calculations such
      as `displaced_volume`.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      self.is_exposed = False
      return self


   def add_attachment_point(self: SymPartSub, attachment_point_id: str, *,
                                              x: Union[float, Expr],
                                              y: Union[float, Expr],
                                              z: Union[float, Expr]) -> SymPartSub:
      """Adds a local attachment point to the SymPart.

      Each coordinate of the attachment point should fall in the range `[0.0, 1.0]` and be
      relative to the *x-axis* length, *y-axis* width, and *z-axis* height of the SymPart with
      its origin at the front, left, center of the part.

      Parameters
      ----------
      attachment_point_id : `str`
         Unique identifier for the new attachment point.
      x : `Union[float, sympy.Expr]`
         Local x-axis placement of the attachment point on the SymPart relative to its length.
      y : `Union[float, sympy.Expr]`
         Local y-axis placement of the attachment point on the SymPart relative to its width.
      z : `Union[float, sympy.Expr]`
         Local z-axis placement of the attachment point on the SymPart relative to its height.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      if attachment_point_id in [point.name for point in self.attachment_points]:
         raise ValueError('An attachment point with the ID "{}" already exists'
                          .format(attachment_point_id))
      self.attachment_points.append(Coordinate(attachment_point_id, x=x, y=y, z=z))
      return self


   def add_connection_port(self: SymPartSub, connection_port_id: str, *,
                                              x: Union[float, Expr],
                                              y: Union[float, Expr],
                                              z: Union[float, Expr]) -> SymPartSub:
      """Adds a local connection port to the SymPart.

      Each coordinate of the connection port should fall in the range `[0.0, 1.0]` and be
      relative to the *x-axis* length, *y-axis* width, and *z-axis* height of the SymPart with
      its origin at the front, left, center of the part.

      Parameters
      ----------
      connection_port_id : `str`
         Unique identifier for the new connection port.
      x : `Union[float, sympy.Expr]`
         Local x-axis placement of the connection port on the SymPart relative to its length.
      y : `Union[float, sympy.Expr]`
         Local y-axis placement of the connection port on the SymPart relative to its width.
      z : `Union[float, sympy.Expr]`
         Local z-axis placement of the connection port on the SymPart relative to its height.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """
      if connection_port_id in [port.name for port in self.connection_ports]:
         raise ValueError('A connection port with the ID "{}" already exists'
                          .format(connection_port_id))
      self.connection_ports.append(Coordinate(connection_port_id, x=x, y=y, z=z))
      return self


   def attach(self: SymPartSub, local_attachment_id: str,
                                remote_part: SymPart,
                                remote_attachment_id: str) -> SymPartSub:
      """Creates a rigid attachment between a local and remote attachment point.

      Parameters
      ----------
      local_attachment_id : `str`
         Identifier of the local attachment point to which to attach.
      remote_part : `SymPart`
         The remote SymPart to which to make an attachment.
      remote_attachment_id : `str`
         Identifier of the remote attachment point to which to attach.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """

      # Ensure that the requested attachment is valid
      if self.name == remote_part.name:
         raise ValueError('The local and attached parts cannot both have the same name "{}"'
                           .format(self.name))
      if local_attachment_id not in [point.name for point in self.attachment_points]:
         raise ValueError('The local attachment point identifier "{}" does not exist'
                           .format(local_attachment_id))
      if remote_attachment_id not in [point.name for point in remote_part.attachment_points]:
         raise ValueError('The remote attachment point identifier "{}" does not exist'
                           .format(remote_attachment_id))
      if local_attachment_id in self.attachments:
         raise ValueError('The local attachment point "{}" is already being used'
                           .format(local_attachment_id))
      if remote_attachment_id in remote_part.attachments:
         raise ValueError('The remote attachment point "{}" is already being used'
                           .format(remote_attachment_id))

      # Make the rigid attachment in both directions
      self.attachments[local_attachment_id] = remote_part.name + '#' + remote_attachment_id
      remote_part.attachments[remote_attachment_id] = self.name + '#' + local_attachment_id
      return self


   def connect(self: SymPartSub, local_connection_id: str,
                                 remote_part: SymPart,
                                 remote_connection_id: str) -> SymPartSub:
      """Creates a non-rigid connection between a local and remote connection port.

      Parameters
      ----------
      local_connection_id : `str`
         Identifier of the local connection port to which to connect.
      remote_part : `SymPart`
         The remote SymPart to which to make a connection.
      remote_connection_id : `str`
         Identifier of the remote connection port to which to connect.

      Returns
      -------
      self : `SymPart`
         The current SymPart being manipulated.
      """

      # Ensure that the requested connection is valid
      if self.name == remote_part.name:
         raise ValueError('The local and connected parts cannot both have the same name "{}"'
                           .format(self.name))
      if local_connection_id not in [port.name for port in self.connection_ports]:
         raise ValueError('The local connection port identifier "{}" does not exist'
                           .format(local_connection_id))
      if remote_connection_id not in [port.name for port in remote_part.connection_ports]:
         raise ValueError('The remote connection port identifier "{}" does not exist'
                           .format(remote_connection_id))
      if local_connection_id in self.connections:
         raise ValueError('The local connection port "{}" is already being used'
                           .format(local_connection_id))
      if remote_connection_id in remote_part.connections:
         raise ValueError('The remote connection port "{}" is already being used'
                           .format(remote_connection_id))

      # Make the flexible connection in both directions
      self.connections[local_connection_id] = remote_part.name + '#' + remote_connection_id
      remote_part.connections[remote_connection_id] = self.name + '#' + local_connection_id
      return self


   def get_cad_physical_properties(self,
                                   normalize_origin: Optional[bool] = False) -> Dict[str, float]:
      """Retrieves the set of physical properties of the SymPart as reported by the underlying
      CAD model.

      Parameters
      ----------
      normalize_origin : `bool`, optional, default=False
         Return physical properties with respect to the front, left, bottom corner of the
         underlying CAD model.

      Returns
      -------
      `Dict[str, float]`
         A list of physical properties as calculated from the underlying CAD model.
      """
      placement_center = self.static_origin.as_tuple() if \
                            self.static_origin is not None else \
                         (0.0, 0.0, 0.0)
      return self.__cad__.get_physical_properties(self.geometry.__dict__,
                                                  placement_center,
                                                  self.orientation.as_tuple(),
                                                  self.material_density,
                                                  normalize_origin)


   def export(self, save_path: str, export_type: Literal['freecad', 'step', 'stl']) -> None:
      """Exports the SymPart to an external CAD representation.

      Supported CAD model formats currently include FreeCAD, STEP, and STL.

      Parameters
      ----------
      save_path : `str`
         Output file path at which to store the the generated CAD model.
      export_type : {'freecad', 'step', 'stl'}
         Format of the CAD model to export.
      """
      placement_center = self.static_origin.as_tuple() if \
                            self.static_origin is not None else \
                         (0.0, 0.0, 0.0)
      self.__cad__.export_model(save_path,
                                export_type,
                                self.geometry.__dict__,
                                placement_center,
                                self.orientation.as_tuple())


   # Abstract methods to be overridden ------------------------------------------------------------

   @abc.abstractmethod
   def set_geometry(self: SymPartSub, **kwargs) -> SymPartSub:
      """Abstract method that must be overridden by a concrete `SymPart` class to allow setting
      its physical geometry.

      Parameters
      ----------
      **kwargs : `Dict`
         Set of named parameters that define the geometry of a SymPart.

      Raises
      -------
      NotImplementedError
         If the implementing `SymPart` class does not override this method.
      """
      raise NotImplementedError

   def get_valid_states(self: SymPartSub) -> List[str]:
      """Method that may be overridden by a concrete `SymPart` class to indicate the list of
      geometric state names recognized by the part.

      If this method is not overridden, it will return an empty list, indicating that the part
      only has one valid geometric state.
      """
      return []


   # Abstract properties that must be overridden --------------------------------------------------

   @property
   def mass(self) -> Union[float, Expr]:
      """Mass (in `kg`) of the SymPart (read-only)."""
      return self.material_volume * self.material_density

   @property
   @abc.abstractmethod
   def material_volume(self) -> Union[float, Expr]:
      """Material volume (in `m^3`) of the SymPart (read-only)."""
      raise NotImplementedError

   @property
   @abc.abstractmethod
   def displaced_volume(self) -> Union[float, Expr]:
      """Displaced volume (in `m^3`) of the SymPart (read-only)."""
      raise NotImplementedError

   @property
   @abc.abstractmethod
   def surface_area(self) -> Union[float, Expr]:
      """Surface/wetted area (in `m^2`) of the SymPart (read-only)."""
      raise NotImplementedError

   @property
   @abc.abstractmethod
   def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                   Union[float, Expr],
                                                   Union[float, Expr]]:
      """Center of gravity (in `m`) of the **unoriented** SymPart (read-only)."""
      raise NotImplementedError

   @property
   def oriented_center_of_gravity(self) -> Tuple[Union[float, Expr],
                                                 Union[float, Expr],
                                                 Union[float, Expr]]:
      """Center of gravity (in `m`) of the **oriented** SymPart (read-only)."""
      origin = self.static_origin.clone() \
                  if self.static_origin is not None else \
               Coordinate(self.name + '_origin')
      center_of_gravity = self.unoriented_center_of_gravity
      center_of_gravity = [center_of_gravity[0] - (origin.x * self.unoriented_length),
                           center_of_gravity[1] - (origin.y * self.unoriented_width),
                           center_of_gravity[2] - (origin.z * self.unoriented_height)]
      return self.orientation.rotate_point((0.0, 0.0, 0.0), center_of_gravity)

   @property
   @abc.abstractmethod
   def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                    Union[float, Expr],
                                                    Union[float, Expr]]:
      """Center of buoyancy (in `m`) of the **unoriented** SymPart (read-only)."""
      raise NotImplementedError

   @property
   def oriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr],
                                                  Union[float, Expr],
                                                  Union[float, Expr]]:
      """Center of buoyancy (in `m`) of the **oriented** SymPart (read-only)."""
      origin = self.static_origin.clone() \
                  if self.static_origin is not None else \
               Coordinate(self.name + '_origin')
      center_of_buoyancy = self.unoriented_center_of_buoyancy
      center_of_buoyancy = [center_of_buoyancy[0] - (origin.x * self.unoriented_length),
                            center_of_buoyancy[1] - (origin.y * self.unoriented_width),
                            center_of_buoyancy[2] - (origin.z * self.unoriented_height)]
      return self.orientation.rotate_point((0.0, 0.0, 0.0), center_of_buoyancy)

   @property
   @abc.abstractmethod
   def unoriented_length(self) -> Union[float, Expr]:
      """X-axis length (in `m`) of the bounding box of the **unoriented** SymPart (read-only)."""
      raise NotImplementedError

   @property
   @abc.abstractmethod
   def unoriented_width(self) -> Union[float, Expr]:
      """Y-axis width (in `m`) of the bounding box of the **unoriented** SymPart (read-only)."""
      raise NotImplementedError

   @property
   @abc.abstractmethod
   def unoriented_height(self) -> Union[float, Expr]:
      """Z-axis height (in `m`) of the bounding box of the **unoriented** SymPart (read-only)."""
      raise NotImplementedError

   @property
   def oriented_length(self) -> Union[float, Expr]:
      """X-axis length (in `m`) of the bounding box of the **oriented** SymPart (read-only)."""
      # TODO: Implement this
      raise NotImplementedError

   @property
   def oriented_width(self) -> Union[float, Expr]:
      """Y-axis width (in `m`) of the bounding box of the **oriented** SymPart (read-only)."""
      # TODO: Implement this
      raise NotImplementedError

   @property
   def oriented_height(self) -> Union[float, Expr]:
      """Z-axis height (in `m`) of the bounding box of the **oriented** SymPart (read-only)."""
      # TODO: Implement this
      raise NotImplementedError
