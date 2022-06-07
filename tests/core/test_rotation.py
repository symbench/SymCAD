#!/usr/bin/env python3

from symcad.core import Rotation
from sympy import Expr, Symbol
from copy import deepcopy
import math

if __name__ == '__main__':

   # Test default symbolic instance construction
   default_id = 'default'
   default_rotation = Rotation(default_id)
   assert default_rotation.name == default_id
   assert isinstance(default_rotation.roll, float)
   assert isinstance(default_rotation.pitch, float)
   assert isinstance(default_rotation.yaw, float)
   assert default_rotation.roll == 0.0
   assert default_rotation.pitch == 0.0
   assert default_rotation.yaw == 0.0

   # Test explicit symbolic instance construction
   symbolic_id = 'symbolic'
   symbolic_rotation = Rotation(symbolic_id, roll=Symbol('roll'), pitch=Symbol('pitch'), yaw=Symbol('yaw'))
   assert symbolic_rotation.name == symbolic_id
   assert isinstance(symbolic_rotation.roll, Expr)
   assert isinstance(symbolic_rotation.pitch, Expr)
   assert isinstance(symbolic_rotation.yaw, Expr)
   assert symbolic_rotation.roll == Symbol('roll')
   assert symbolic_rotation.pitch == Symbol('pitch')
   assert symbolic_rotation.yaw == Symbol('yaw')

   # Test concrete instance construction
   concrete_id = 'concrete'
   concrete_rotation = Rotation(concrete_id, roll=1.0, pitch=2.0, yaw=3.0)
   assert concrete_rotation.name == concrete_id
   assert isinstance(concrete_rotation.roll, float)
   assert isinstance(concrete_rotation.pitch, float)
   assert isinstance(concrete_rotation.yaw, float)
   assert concrete_rotation.roll == 1.0
   assert concrete_rotation.pitch == 2.0
   assert concrete_rotation.yaw == 3.0

   # Test cloning concrete rotations
   cloned_rotation = concrete_rotation.clone()
   assert cloned_rotation.name == concrete_id
   assert isinstance(cloned_rotation.roll, float)
   assert isinstance(cloned_rotation.pitch, float)
   assert isinstance(cloned_rotation.yaw, float)
   assert cloned_rotation.roll == 1.0
   assert cloned_rotation.pitch == 2.0
   assert cloned_rotation.yaw == 3.0
   assert cloned_rotation == concrete_rotation
   assert cloned_rotation != symbolic_rotation

   # Test cloning symbolic rotations
   cloned_rotation = symbolic_rotation.clone()
   assert cloned_rotation.name == symbolic_id
   assert isinstance(cloned_rotation.roll, Expr)
   assert isinstance(cloned_rotation.pitch, Expr)
   assert isinstance(cloned_rotation.yaw, Expr)
   assert cloned_rotation.roll == Symbol('roll')
   assert cloned_rotation.pitch == Symbol('pitch')
   assert cloned_rotation.yaw == Symbol('yaw')
   assert cloned_rotation == symbolic_rotation
   assert cloned_rotation != concrete_rotation

   # Test cloning concrete rotations using the copy library
   cloned_rotation = deepcopy(concrete_rotation)
   assert cloned_rotation.name == concrete_id
   assert isinstance(cloned_rotation.roll, float)
   assert isinstance(cloned_rotation.pitch, float)
   assert isinstance(cloned_rotation.yaw, float)
   assert cloned_rotation.roll == 1.0
   assert cloned_rotation.pitch == 2.0
   assert cloned_rotation.yaw == 3.0
   assert cloned_rotation == concrete_rotation
   assert cloned_rotation != symbolic_rotation

   # Test cloning symbolic rotations using the copy library
   cloned_rotation = deepcopy(symbolic_rotation)
   assert cloned_rotation.name == symbolic_id
   assert isinstance(cloned_rotation.roll, Expr)
   assert isinstance(cloned_rotation.pitch, Expr)
   assert isinstance(cloned_rotation.yaw, Expr)
   assert cloned_rotation.roll == Symbol('roll')
   assert cloned_rotation.pitch == Symbol('pitch')
   assert cloned_rotation.yaw == Symbol('yaw')
   assert cloned_rotation == symbolic_rotation
   assert cloned_rotation != concrete_rotation

   # Test copying concrete rotations
   copied_id = 'copied'
   copied_rotation = Rotation(copied_id).copy_from(concrete_rotation)
   assert copied_rotation.name == copied_id
   assert isinstance(copied_rotation.roll, float)
   assert isinstance(copied_rotation.pitch, float)
   assert isinstance(copied_rotation.yaw, float)
   assert copied_rotation.roll == 1.0
   assert copied_rotation.pitch == 2.0
   assert copied_rotation.yaw == 3.0
   assert copied_rotation == concrete_rotation
   assert copied_rotation != symbolic_rotation

   # Test copying symbolic rotations
   copied_rotation.copy_from(symbolic_rotation)
   assert copied_rotation.name == copied_id
   assert isinstance(copied_rotation.roll, Expr)
   assert isinstance(copied_rotation.pitch, Expr)
   assert isinstance(copied_rotation.yaw, Expr)
   assert copied_rotation.roll == Symbol('roll')
   assert copied_rotation.pitch == Symbol('pitch')
   assert copied_rotation.yaw == Symbol('yaw')
   assert copied_rotation == symbolic_rotation
   assert copied_rotation != concrete_rotation

   # Test clearing and setting rotations
   cleared_rotation = copied_rotation.clear()
   assert cleared_rotation.name == copied_rotation.name
   assert cleared_rotation.roll == 0.0
   assert cleared_rotation.pitch == 0.0
   assert cleared_rotation.yaw == 0.0
   set_concrete_rotation = cleared_rotation.set(roll_deg=3.0, pitch_deg=2.0, yaw_deg=1.0)
   assert set_concrete_rotation.name == cleared_rotation.name
   assert abs(set_concrete_rotation.roll - math.radians(3.0)) < 0.00001
   assert abs(set_concrete_rotation.pitch - math.radians(2.0)) < 0.00001
   assert abs(set_concrete_rotation.yaw - math.radians(1.0)) < 0.00001
   set_symbolic_rotation = cleared_rotation.set(roll_deg=None, pitch_deg=None, yaw_deg=None)
   assert set_symbolic_rotation.name == cleared_rotation.name
   assert set_symbolic_rotation.roll == Symbol(set_symbolic_rotation.name + '_roll')
   assert set_symbolic_rotation.pitch == Symbol(set_symbolic_rotation.name + '_pitch')
   assert set_symbolic_rotation.yaw == Symbol(set_symbolic_rotation.name + '_yaw')
   set_symbolic_rotation = cleared_rotation\
      .set(roll_deg=Symbol('roll_deg'), pitch_deg=Symbol('pitch_deg'), yaw_deg=Symbol('yaw_deg'))
   assert set_symbolic_rotation.name == cleared_rotation.name
   assert set_symbolic_rotation.roll == Symbol('roll_deg') * math.pi / 180.0
   assert set_symbolic_rotation.pitch == Symbol('pitch_deg') * math.pi / 180.0
   assert set_symbolic_rotation.yaw == Symbol('yaw_deg') * math.pi / 180.0

   # Test creating a Rotation object from the angular factory method
   rotation_direct = Rotation.from_angles('test_direct', math.pi / 2.0, math.pi / 3.0, math.pi / 4.0)
   assert rotation_direct.roll == math.pi / 2.0
   assert rotation_direct.pitch == math.pi / 3.0
   assert rotation_direct.yaw == math.pi / 4.0

   # Test creating a Rotation object from the quaternion factory method
   rotation_quat = Rotation.from_quaternion('test_quat', rotation_direct.get_quaternion())
   assert abs(rotation_quat.roll - math.pi / 2.0) < 0.00001
   assert abs(rotation_quat.pitch - math.pi / 3.0) < 0.00001
   assert abs(rotation_quat.yaw - math.pi / 4.0) < 0.00001

   # Test creating a Rotation object from the rotation matrix factory method
   rotation_rot = Rotation.from_rotation_matrix('test_rot', rotation_direct.get_rotation_matrix())
   assert abs(rotation_rot.roll - math.pi / 2.0) < 0.00001
   assert abs(rotation_rot.pitch - math.pi / 3.0) < 0.00001
   assert abs(rotation_rot.yaw - math.pi / 4.0) < 0.00001

   # Test generating a quaternion
   quaternion = rotation_direct.get_quaternion()
   assert abs(quaternion[0] - 0.701057384649978) < 0.00001
   assert abs(quaternion[1] - 0.430459334576879) < 0.00001
   assert abs(quaternion[2] - 0.560985526796931) < 0.00001
   assert abs(quaternion[3] + 0.0922959556412571) < 0.00001

   # Test generating a rotation matrix
   rotation_matrix = rotation_direct.get_rotation_matrix()
   assert abs(rotation_matrix[0][0] - 0.353553390593274) < 0.00001
   assert abs(rotation_matrix[0][1] - 0.612372435695795) < 0.00001
   assert abs(rotation_matrix[0][2] - 0.707106781186547) < 0.00001
   assert abs(rotation_matrix[1][0] - 0.353553390593274) < 0.00001
   assert abs(rotation_matrix[1][1] - 0.612372435695795) < 0.00001
   assert abs(rotation_matrix[1][2] + 0.707106781186548) < 0.00001
   assert abs(rotation_matrix[2][0] + 0.866025403784439) < 0.00001
   assert abs(rotation_matrix[2][1] - 0.500000000000000) < 0.00001
   assert abs(rotation_matrix[2][2] - 0.000000000000000) < 0.00001

   # Print out the rotation matrix
#    max_len = str(5 + max([len(str(rotation_matrix[i][j])) for i in range(3) for j in range(3)]))
#    print(('[{:>'+max_len+'} {:>'+max_len+'} {:>'+max_len+'}\n' + \
#             ' {:>'+max_len+'} {:>'+max_len+'} {:>'+max_len+'}\n' + \
#             ' {:>'+max_len+'} {:>'+max_len+'} {:>'+max_len+'}]')\
#       .format(str(rotation_matrix[0][0]), str(rotation_matrix[0][1]), str(rotation_matrix[0][2]),
#               str(rotation_matrix[1][0]), str(rotation_matrix[1][1]), str(rotation_matrix[1][2]),
#               str(rotation_matrix[2][0]), str(rotation_matrix[2][1]), str(rotation_matrix[2][2])))

   # Test rotating a point around a specified center of rotation
   test_rotation = Rotation('test', roll=math.radians(30.0), pitch=math.radians(0.0), yaw=math.radians(0.0))
   center_of_rotation = (0.2, 0.4, 0.6)
   rotated_point = (1.4, 2.7, 3.7)
   rotated_x, rotated_y, rotated_z = test_rotation.rotate_point(center_of_rotation, rotated_point)
   assert abs(rotated_x - 1.40000000000000) < 0.00001
   assert abs(rotated_y - 0.841858428704209) < 0.00001
   assert abs(rotated_z - 4.43467875173176) < 0.00001
   test_rotation = Rotation('test', roll=math.radians(0.0), pitch=math.radians(30.0), yaw=math.radians(0.0))
   rotated_x, rotated_y, rotated_z = test_rotation.rotate_point(center_of_rotation, rotated_point)
   assert abs(rotated_x - 2.78923048454133) < 0.00001
   assert abs(rotated_y - 2.70000000000000) < 0.00001
   assert abs(rotated_z - 2.68467875173176) < 0.00001
   test_rotation = Rotation('test', roll=math.radians(0.0), pitch=math.radians(0.0), yaw=math.radians(30.0))
   rotated_x, rotated_y, rotated_z = test_rotation.rotate_point(center_of_rotation, rotated_point)
   assert abs(rotated_x - 0.0892304845413266) < 0.00001
   assert abs(rotated_y - 2.99185842870421) < 0.00001
   assert abs(rotated_z - 3.70000000000000) < 0.00001
   test_rotation = Rotation('test', roll=math.radians(30.0), pitch=math.radians(30.0), yaw=math.radians(30.0))
   rotated_x, rotated_y, rotated_z = test_rotation.rotate_point(center_of_rotation, rotated_point)
   assert abs(rotated_x - 2.53953539282395) < 0.00001
   assert abs(rotated_y - 2.26094555433772) < 0.00001
   assert abs(rotated_z - 3.32092921435211) < 0.00001
