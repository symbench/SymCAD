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
from typing import List, Tuple, Union
from sympy import Expr, Symbol
from copy import deepcopy
from operator import mul
import math, sympy

Quaternion = Tuple[Union[float, Expr], Union[float, Expr], Union[float, Expr], Union[float, Expr]]

class Rotation(object):
   """Represents a simple right-handed rotation assuming the nautical and aeronautical convention
   of intrinsic `yaw, pitch, roll` rotation order.
   """

   # Public attributes ----------------------------------------------------------------------------

   name: str
   """Unique, identifying name of the `Rotation` instance."""

   roll: Union[float, Expr]
   """Intrinsic roll angle in radians."""

   pitch: Union[float, Expr]
   """Intrinsic pitch angle in radians."""

   yaw: Union[float, Expr]
   """Intrinsic yaw angle in radians."""


   # Constructor and factory methods --------------------------------------------------------------

   def __init__(self, identifier: str, **kwargs) -> None:
      """Initializes a `Rotation` instance, where `identifier` uniquely identifies the instance,
      and `**kwargs` may contain the keywords `roll`, `pitch`, or `yaw` to specify a concrete
      value for each component of the rotation. If any of these keywords are missing, the
      corresponding angle of rotation will be assumed to be `0`.

      Alternately, a `Rotation` instance can be created from:

      - A quaternion,
      - An explicit set of yaw, pitch, and roll angles, or
      - A 3D rotation matrix.

      A quaternion or rotation matrix is retrievable from any `Rotation` instance, regardless of
      how it was created.

      All rotations utilize a right-handed coordinate system and follow the convention of using
      intrinsic rotations in the order `yaw, pitch, roll`. In other words, all rotations move in
      the counter-clockwise direction when viewed from a positive axis looking toward origin,
      first around the z-axis, then the y-axis, and finally around the x-axis.
      """
      super().__init__()
      self.name = identifier
      self.roll = kwargs.get('roll', 0.0)
      self.pitch = kwargs.get('pitch', 0.0)
      self.yaw = kwargs.get('yaw', 0.0)


   @classmethod
   def from_angles(cls, identifier: str,
                        roll_rad: Union[float, Expr, None],
                        pitch_rad: Union[float, Expr, None],
                        yaw_rad: Union[float, Expr, None]) -> Rotation:
      """Constructs a `Rotation` object with the specified roll, pitch, and yaw angles.

      Parameters
      ----------
      roll_rad : `Union[float, sympy.Expr, None]`
         Desired intrinsic roll angle in radians. If `None` is specified, the angle will be
         treated as a symbol.
      pitch_rad : `Union[float, sympy.Expr, None]`
         Desired intrinsic pitch angle in radians. If `None` is specified, the angle will be
         treated as a symbol.
      yaw_rad : `Union[float, sympy.Expr, None]`
         Desired intrinsic yaw angle in radians. If `None` is specified, the angle will be
         treated as a symbol.

      Returns
      -------
      `Rotation`
         The newly created Rotation instance.
      """
      roll = roll_rad if roll_rad is not None else Symbol(identifier + '_roll')
      pitch = pitch_rad if pitch_rad is not None else Symbol(identifier + '_pitch')
      yaw = yaw_rad if yaw_rad is not None else Symbol(identifier + '_yaw')
      return cls(identifier, roll=roll, pitch=pitch, yaw=yaw)


   @classmethod
   def from_quaternion(cls, identifier: str, quaternion: Quaternion) -> Rotation:
      """Constructs a `Rotation` object from the specified quaternion.

      The ordering of the quaternion is expected to be: `q0, q1, q2, q3` or
      equivalently `qw, qx, qy, qz`.

      Parameters
      ----------
      quaternion : `Quaternion`
         Desired quaternion from which to construct a Rotation object.

      Returns
      -------
      `Rotation`
         The newly created Rotation instance.
      """

      # Roll calculation
      sinroll_cospitch = 2.0*(quaternion[0]*quaternion[1] + quaternion[2]*quaternion[3])
      cosroll_cospitch = 1.0 - 2.0*(quaternion[1]*quaternion[1] + quaternion[2]*quaternion[2])
      roll = sympy.atan2(sinroll_cospitch, cosroll_cospitch)

      # Pitch calculation
      sinpitch = 2.0*(quaternion[0]*quaternion[2] - quaternion[3]*quaternion[1])
      pitch = math.copysign(0.5 * math.pi, sinpitch) if not isinstance(sinpitch, Expr) \
                                                        and abs(sinpitch) >= 1.0 else \
              sympy.asin(sinpitch)

      # Yaw calculation
      sinyaw_cospitch = 2.0*(quaternion[0]*quaternion[3] + quaternion[1]*quaternion[2])
      cosyaw_cospitch = 1.0 - 2.0*(quaternion[2]*quaternion[2] + quaternion[3]*quaternion[3])
      yaw = sympy.atan2(sinyaw_cospitch, cosyaw_cospitch)
      return cls(identifier, roll=roll, pitch=pitch, yaw=yaw)


   @classmethod
   def from_rotation_matrix(cls, identifier: str, rotation_matrix: List[List[float]]) -> Rotation:
      """Constructs a `Rotation` object from the specified rotation matrix.

      Parameters
      ----------
      rotation_matrix : `List[List[float]]`
         Desired 3x3 rotation matrix from which to construct a Rotation object.

      Returns
      -------
      `Rotation`
         The newly created Rotation instance.
      """
      roll = sympy.atan2(rotation_matrix[2][1], rotation_matrix[2][2])
      pitch = -sympy.asin(rotation_matrix[2][0])
      yaw = sympy.atan2(rotation_matrix[1][0], rotation_matrix[0][0])
      return cls(identifier, roll=roll, pitch=pitch, yaw=yaw)


   # Built-in method implementations --------------------------------------------------------------

   def __repr__(self) -> str:
      roll = self.roll * 180.0 / math.pi
      pitch = self.pitch * 180.0 / math.pi
      yaw = self.yaw * 180.0 / math.pi
      return 'roll = {}\u00b0, pitch = {}\u00b0, yaw = {}\u00b0'.format(roll, pitch, yaw)

   def __eq__(self, other: Rotation) -> bool:
      return (self.roll == other.roll) and (self.pitch == other.pitch) and (self.yaw == other.yaw)

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


   # Public methods -------------------------------------------------------------------------------

   def clone(self) -> Rotation:
      """Returns an exact clone of this `Rotation` instance."""
      return deepcopy(self)


   def copy_from(self, other: Rotation) -> Rotation:
      """Copies the rotation angles from another `Rotation` instance into this one.

      The name of this instance will not be changed or overwritten.

      Parameters
      ----------
      other : `Rotation`
         A Rotation object whose contents should be copied into this instance.

      Returns
      -------
      self : `Rotation`
         The Rotation instance being manipulated.
      """
      self.roll = other.roll
      self.pitch = other.pitch
      self.yaw = other.yaw
      return self


   def set(self, *, roll_deg: Union[float, Expr, None],
                    pitch_deg: Union[float, Expr, None],
                    yaw_deg: Union[float, Expr, None]) -> Rotation:
      """Sets the roll, pitch, and yaw angles to the specified values.

      Parameters
      ----------
      roll_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic roll angle in degrees. If `None` is specified, the angle will be
         treated as a symbol.
      pitch_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic pitch angle in degrees. If `None` is specified, the angle will be
         treated as a symbol.
      yaw_deg : `Union[float, sympy.Expr, None]`
         Desired intrinsic yaw angle in degrees. If `None` is specified, the angle will be
         treated as a symbol.

      Returns
      -------
      self : `Rotation`
         The Rotation instance being manipulated.
      """
      self.roll = Symbol(self.name + '_roll') if roll_deg is None else \
                  roll_deg * math.pi / 180.0
      self.pitch = Symbol(self.name + '_pitch') if pitch_deg is None else \
                   pitch_deg * math.pi / 180.0
      self.yaw = Symbol(self.name + '_yaw') if yaw_deg is None else \
                 yaw_deg * math.pi / 180.0
      return self


   def clear(self) -> Rotation:
      """Clears all rotation angles to `0` degrees.

      Returns
      -------
      self : `Rotation`
         The Rotation instance being manipulated.
      """
      self.roll = self.pitch = self.yaw = 0.0
      return self


   def rotate_point(self, rotation_center: Tuple[float, float, float],
                          point: Tuple[float, float, float]) -> Tuple[float, float, float]:
      """Rotates a `point` around its `rotation_center` according to the current `Rotation`
      instance properties.

      Parameters
      ----------
      rotation_center : `Tuple[float, float, float]`
         Cartestion coordinate around which to carry out the specified rotation.
      point : `Tuple[float, float, float]`
         The Cartesian coordinates of the point to be rotated.

      Returns
      -------
      `Tuple[float, float, float]`
         The final Cartesian coordinates of the rotated point.
      """
      R = self.get_rotation_matrix()
      centered_point = [point[i] - rotation_center[i] for i in range(3)]
      rotated_point = [sum(map(mul, R[i], centered_point)) for i in range(3)]
      return tuple([rotation_center[i] + rotated_point[i] for i in range(3)])


   def get_quaternion(self) -> Quaternion:
      """Returns a quaternion representing the `Rotation` object.

      The ordering of the quaternion will be: `q0, q1, q2, q3` or
      equivalently `qw, qx, qy, qz`.

      Returns
      -------
      `Quaternion`
         A quaternion representing this Rotation object.
      """
      half_roll = 0.5 * self.roll
      half_pitch = 0.5 * self.pitch
      half_yaw = 0.5 * self.yaw
      s = sympy.cos(half_roll) * sympy.cos(half_pitch) * sympy.cos(half_yaw) \
          + sympy.sin(half_roll) * sympy.sin(half_pitch) * sympy.sin(half_yaw)
      q1 = sympy.sin(half_roll) * sympy.cos(half_pitch) * sympy.cos(half_yaw) \
           - sympy.cos(half_roll) * sympy.sin(half_pitch) * sympy.sin(half_yaw)
      q2 = sympy.cos(half_roll) * sympy.sin(half_pitch) * sympy.cos(half_yaw) \
           + sympy.sin(half_roll) * sympy.cos(half_pitch) * sympy.sin(half_yaw)
      q3 = sympy.cos(half_roll) * sympy.cos(half_pitch) * sympy.sin(half_yaw) \
           - sympy.sin(half_roll) * sympy.sin(half_pitch) * sympy.cos(half_yaw)
      return s, q1, q2, q3


   def get_rotation_matrix(self) -> List[List[float]]:
      """Returns a 3D rotation matrix representing the `Rotation` object.

      Returns
      -------
      `List[List[float]]`
         A 3x3 rotation matrix representing this Rotation object.
      """
      rotation_matrix00 = sympy.cos(self.pitch)*sympy.cos(self.yaw)
      rotation_matrix01 = sympy.sin(self.roll)*sympy.sin(self.pitch)*sympy.cos(self.yaw) \
                          - sympy.sin(self.yaw)*sympy.cos(self.roll)
      rotation_matrix02 = sympy.sin(self.roll)*sympy.sin(self.yaw) \
                          + sympy.sin(self.pitch)*sympy.cos(self.roll)*sympy.cos(self.yaw)
      rotation_matrix10 = sympy.sin(self.yaw)*sympy.cos(self.pitch)
      rotation_matrix11 = sympy.sin(self.roll)*sympy.sin(self.pitch)*sympy.sin(self.yaw) \
                          + sympy.cos(self.roll)*sympy.cos(self.yaw)
      rotation_matrix12 = sympy.sin(self.pitch)*sympy.sin(self.yaw)*sympy.cos(self.roll) \
                          - sympy.sin(self.roll)*sympy.cos(self.yaw)
      rotation_matrix20 = -sympy.sin(self.pitch)
      rotation_matrix21 = sympy.sin(self.roll)*sympy.cos(self.pitch)
      rotation_matrix22 = sympy.cos(self.roll)*sympy.cos(self.pitch)
      return [[rotation_matrix00, rotation_matrix01, rotation_matrix02],
              [rotation_matrix10, rotation_matrix11, rotation_matrix12],
              [rotation_matrix20, rotation_matrix21, rotation_matrix22]]
