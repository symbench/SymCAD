#!/usr/bin/env python3

from symcad.parts.generic import Box, Capsule, Cone, Cuboid, Cylinder, EllipsoidalCap, EllipticCylinder
from symcad.parts.generic import EllipticPipe, Parallelepiped, Pipe, Prism, Pyramid, Sphere, Torus
from symcad.parts.endcaps import ConicalFrustrum, FlangedFlatPlate, Hemisphere, Semiellipsoid, Torisphere

def export_generic_cad_shapes():

   shape = Box('test').set_geometry(length_m=3, width_m=2, height_m=1, thickness_m=0.01)
   shape.export('box.FCStd', 'freecad')
   shape = Capsule('test').set_geometry(cylinder_radius_m=1, cylinder_length_m=2, endcap_length_m=0.5, thickness_m=0.01)
   shape.export('capsule.FCStd', 'freecad')
   shape = Cone('test').set_geometry(bottom_radius_m=3, top_radius_m=1, height_m=2)
   shape.export('cone.FCStd', 'freecad')
   shape = Cuboid('test').set_geometry(length_m=3, width_m=2, height_m=1)
   shape.export('cuboid.FCStd', 'freecad')
   shape = Cylinder('test').set_geometry(radius_m=1, height_m=3)
   shape.export('cylinder.FCStd', 'freecad')
   shape = EllipsoidalCap('test').set_geometry(major_radius_m=1.3, minor_radius_m=0.5, height_m=0.3)
   shape.export('ellipsoidalcap.FCStd', 'freecad')
   shape = EllipticCylinder('test').set_geometry(major_radius_m=1.3, minor_radius_m=0.5, height_m=3)
   shape.export('ellipticcylinder.FCStd', 'freecad')
   shape = EllipticPipe('test').set_geometry(major_radius_m=1.3, minor_radius_m=0.5, height_m=3, thickness_m=0.01)
   shape.export('ellipticpipe.FCStd', 'freecad')
   shape = Parallelepiped('test').set_geometry(length_m=3, width_m=2, height_m=2, length_height_angle_rad=math.radians(75.0))
   shape.export('parallelepiped.FCStd', 'freecad')
   shape = Pipe('test').set_geometry(radius_m=1, height_m=3, thickness_m=0.01)
   shape.export('pipe.FCStd', 'freecad')
   shape = Prism('test').set_geometry(num_edges=6, edge_length_m=1, height_m=3)
   shape.export('prism.FCStd', 'freecad')
   shape = Pyramid('test').set_geometry(num_edges=6, edge_length_m=1, height_m=3)
   shape.export('pyramid.FCStd', 'freecad')
   shape = Sphere('test').set_geometry(radius_m=1)
   shape.export('sphere.FCStd', 'freecad')
   shape = Torus('test').set_geometry(hole_radius_m=1, tube_radius_m=0.2)
   shape.export('torus.FCStd', 'freecad')

def export_endcap_cad_shapes():

   shape = ConicalFrustrum('test').set_geometry(bottom_radius_m=3, top_radius_m=1, height_m=2, thickness_m=0.01)
   shape.export('conicalfrustrum.FCStd', 'freecad')
   shape = FlangedFlatPlate('test').set_geometry(radius_m=1.0, flange_radius_m=0.2, thickness_m=0.01)
   shape.export('flangedflatplate.FCStd', 'freecad')
   shape = Hemisphere('test').set_geometry(radius_m=1.0, thickness_m=0.01)
   shape.export('hemisphere.FCStd', 'freecad')
   shape = Semiellipsoid('test').set_geometry(major_axis_length_m=0.5, minor_axis_radius_m=1.0, thickness_m=0.01)
   shape.export('semiellipsoid.FCStd', 'freecad')
   shape = Torisphere('test').set_geometry(base_radius_m=1.0, thickness_m=0.01)
   shape.export('torisphere.FCStd', 'freecad')


if __name__ == '__main__':

   export_generic_cad_shapes()
   export_endcap_cad_shapes()
