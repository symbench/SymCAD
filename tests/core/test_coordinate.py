#!/usr/bin/env python3

from symcad.core import Coordinate
from sympy import Expr, Symbol

if __name__ == '__main__':

   # Test default symbolic instance construction
   symbolic_id = 'symbolic'
   symbolic_coordinate = Coordinate(symbolic_id)
   assert symbolic_coordinate.name == symbolic_id
   assert isinstance(symbolic_coordinate.x, Expr)
   assert isinstance(symbolic_coordinate.y, Expr)
   assert isinstance(symbolic_coordinate.z, Expr)
   assert symbolic_coordinate.x == Symbol(symbolic_id + '_x')
   assert symbolic_coordinate.y == Symbol(symbolic_id + '_y')
   assert symbolic_coordinate.z == Symbol(symbolic_id + '_z')

   # Test partially explicit symbolic instance construction
   symbolic_coordinate = Coordinate(symbolic_id, x=Symbol('x'), y=Symbol('y'))
   assert symbolic_coordinate.name == symbolic_id
   assert isinstance(symbolic_coordinate.x, Expr)
   assert isinstance(symbolic_coordinate.y, Expr)
   assert isinstance(symbolic_coordinate.z, Expr)
   assert symbolic_coordinate.x == Symbol('x')
   assert symbolic_coordinate.y == Symbol('y')
   assert symbolic_coordinate.z == Symbol(symbolic_id + '_z')

   # Test concrete instance construction
   concrete_id = 'concrete'
   concrete_coordinate = Coordinate(concrete_id, x=1.0, y=2.0, z=3.0)
   assert concrete_coordinate.name == concrete_id
   assert isinstance(concrete_coordinate.x, float)
   assert isinstance(concrete_coordinate.y, float)
   assert isinstance(concrete_coordinate.z, float)
   assert concrete_coordinate.x == 1.0
   assert concrete_coordinate.y == 2.0
   assert concrete_coordinate.z == 3.0

   # Test cloning concrete coordinates
   cloned_coordinate = concrete_coordinate.clone()
   assert cloned_coordinate.name == concrete_coordinate.name
   assert isinstance(cloned_coordinate.x, float)
   assert isinstance(cloned_coordinate.y, float)
   assert isinstance(cloned_coordinate.z, float)
   assert cloned_coordinate.x == 1.0
   assert cloned_coordinate.y == 2.0
   assert cloned_coordinate.z == 3.0
   assert cloned_coordinate == concrete_coordinate
   assert cloned_coordinate != symbolic_coordinate

   # Test cloning symbolic coordinates
   cloned_coordinate = symbolic_coordinate.clone()
   assert cloned_coordinate.name == symbolic_coordinate.name
   assert isinstance(cloned_coordinate.x, Expr)
   assert isinstance(cloned_coordinate.y, Expr)
   assert isinstance(cloned_coordinate.z, Expr)
   assert cloned_coordinate.x == Symbol('x')
   assert cloned_coordinate.y == Symbol('y')
   assert cloned_coordinate.z == Symbol(symbolic_id + '_z')
   assert cloned_coordinate != concrete_coordinate
   assert cloned_coordinate == symbolic_coordinate

   # Test copying concrete coordinates
   copied_id = 'copied'
   copied_coordinate = Coordinate(copied_id).copy_from(concrete_coordinate)
   assert copied_coordinate.name == copied_id
   assert isinstance(copied_coordinate.x, float)
   assert isinstance(copied_coordinate.y, float)
   assert isinstance(copied_coordinate.z, float)
   assert copied_coordinate.x == 1.0
   assert copied_coordinate.y == 2.0
   assert copied_coordinate.z == 3.0
   assert copied_coordinate == concrete_coordinate
   assert copied_coordinate != symbolic_coordinate

   # Test copying symbolic coordinates
   copied_coordinate.copy_from(symbolic_coordinate)
   assert copied_coordinate.name == copied_id
   assert isinstance(copied_coordinate.x, Expr)
   assert isinstance(copied_coordinate.y, Expr)
   assert isinstance(copied_coordinate.z, Expr)
   assert copied_coordinate.x == Symbol('x')
   assert copied_coordinate.y == Symbol('y')
   assert copied_coordinate.z == Symbol(symbolic_id + '_z')
   assert copied_coordinate != concrete_coordinate
   assert copied_coordinate == symbolic_coordinate

   # Test clearing and setting coordinates
   cleared_coordinate = copied_coordinate.clear()
   assert cleared_coordinate.name == copied_coordinate.name
   assert cleared_coordinate.x == 0.0
   assert cleared_coordinate.y == 0.0
   assert cleared_coordinate.z == 0.0
   set_concrete_coordinate = cleared_coordinate.set(x=3.0, y=2.0, z=1.0)
   assert set_concrete_coordinate.name == cleared_coordinate.name
   assert set_concrete_coordinate.x == 3.0
   assert set_concrete_coordinate.y == 2.0
   assert set_concrete_coordinate.z == 1.0
   set_symbolic_coordinate = cleared_coordinate.set(x=None, y=None, z=Symbol('z'))
   assert set_symbolic_coordinate.name == cleared_coordinate.name
   assert set_symbolic_coordinate.x == Symbol(set_symbolic_coordinate.name + '_x')
   assert set_symbolic_coordinate.y == Symbol(set_symbolic_coordinate.name + '_y')
   assert set_symbolic_coordinate.z == Symbol('z')

   # Test returning coordinates as a tuple
   tuple_x, tuple_y, tuple_z = concrete_coordinate.as_tuple()
   assert tuple_x == 1.0
   assert tuple_y == 2.0
   assert tuple_z == 3.0
