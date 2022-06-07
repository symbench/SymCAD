#!/usr/bin/env python3

from symcad.core import Geometry
from copy import deepcopy
from sympy import Symbol

if __name__ == '__main__':

   # Test instance construction
   geometry_id = 'test_geometry'
   geometry = Geometry(geometry_id)
   assert geometry.name == geometry_id

   # Test adding instance attributes
   setattr(geometry, 'radius', Symbol(geometry_id + '_radius'))
   setattr(geometry, 'length', 1.0)
   assert isinstance(geometry.radius, Symbol)
   assert isinstance(geometry.length, float)
   assert geometry.radius == Symbol(geometry_id + '_radius')
   assert geometry.length == 1.0

   # Test cloning a geometry
   cloned_geometry = geometry.clone()
   assert cloned_geometry.name == geometry_id
   assert isinstance(cloned_geometry.radius, Symbol)
   assert isinstance(cloned_geometry.length, float)
   assert cloned_geometry.radius == Symbol(geometry_id + '_radius')
   assert cloned_geometry.length == 1.0
   assert cloned_geometry == geometry

   # Test cloning a geometry using the copy library
   cloned_geometry = deepcopy(geometry)
   assert cloned_geometry.name == geometry_id
   assert isinstance(cloned_geometry.radius, Symbol)
   assert isinstance(cloned_geometry.length, float)
   assert cloned_geometry.radius == Symbol(geometry_id + '_radius')
   assert cloned_geometry.length == 1.0
   assert cloned_geometry == geometry

   # Test copying geometric properties
   copied_id = 'copied_geometry'
   copied_geometry = Geometry(copied_id).copy_from(geometry)
   assert copied_geometry.name == copied_id
   assert isinstance(copied_geometry.radius, Symbol)
   assert isinstance(copied_geometry.length, float)
   assert copied_geometry.radius == Symbol(geometry_id + '_radius')
   assert copied_geometry.length == 1.0
   assert copied_geometry == geometry

   # Test clearing and setting geometric properties
   cleared_geometry = copied_geometry.clear()
   assert cleared_geometry.name == copied_geometry.name
   assert cleared_geometry.radius == 0.0
   assert cleared_geometry.length == 0.0
   set_geometry = cleared_geometry.set()
   assert set_geometry.name == copied_geometry.name
   assert set_geometry.radius == Symbol(set_geometry.name + '_radius')
   assert set_geometry.length == Symbol(set_geometry.name + '_length')
   set_geometry = cleared_geometry.set(radius=2.0)
   assert set_geometry.name == copied_geometry.name
   assert set_geometry.radius == 2.0
   assert set_geometry.length == Symbol(set_geometry.name + '_length')
   set_geometry = cleared_geometry.set(radius=2.0, length=Symbol('new_length'))
   assert set_geometry.name == copied_geometry.name
   assert set_geometry.radius == 2.0
   assert set_geometry.length == Symbol('new_length')

   # Test built-in mathematical properties
   set_geometry *= 2.0
   assert set_geometry.radius == 4.0
   assert set_geometry.length == 2.0 * Symbol('new_length')
   set_geometry /= 2.0
   assert set_geometry.radius == 2.0
   assert set_geometry.length == 1.0 * Symbol('new_length')
