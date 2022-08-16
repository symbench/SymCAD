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
# What is SymCAD?

SymCAD is a Python library that combines symbolic model creation, orientation, and assembly with
concrete CAD representations and manipulations. It allows users to programmatically design
individual shape-based parts, ranging from the very simple and generic to the complex and
specific, while allowing parameters related to the geometry, orientation, and placement
of a part to be expressed symbolically.

Notable features of the library include:

  - Utilizes the Python [sympy](https://www.sympy.org) library for symbolic manipulation of
    parameters
  - Utilizes the [FreeCAD](https://www.freecadweb.org/) Python backend for CAD file processing
    and manipulation
  - Works with both [scripted](#create-a-new-scripted-symcad-part) and
    [modeled](#create-a-new-modeled-symcad-part) CAD designs
  - Provides two methods of model construction:
    1. [Assembly-by-Placement](#create-an-assembly-using-assembly-by-placement): Part placement
       is explicitly defined
    2. [Assembly-by-Attachment](#create-an-assembly-using-assembly-by-attachment): Part placement
       is implicit based on rigidly attached parts
  - Includes a built-in library of generic parts
  - [JSON-based Graph API](#create-a-design-using-the-json-graph-api) for design representation
  - Specification of center-of-placement/origin for each part
  - Custom attachment and connection points for each part
  - Part-based [physical property retrieval](#retrieve-physical-properties-from-a-part):
    1. Based on closed-form equations (concrete or symbolic)
    2. Based on CAD representations (concrete)
    3. Based on pretrained neural networks (concrete or symbolic)
  - Assembly-based cumulative
    [physical property retrieval](#retrieve-physical-properties-from-an-assembly)
  - Physical properties include: mass, material volume, displaced volume, surface area,
    center of gravity, center of buoyancy, length, width, and height
  - [Part importation](#import-an-existing-cad-model) from existing CAD models
    (FreeCAD, STEP, or STL)
  - [Interference detection](#detect-part-interferences-within-an-assembly) for parts within
    an assembly
  - Easy-to-create custom parts (scripted or modeled)
  - Automatic separation of regular and displacement models
  - Parts and assemblies exportable to FreeCAD, STEP, or STL
  - [State-based physical properties](#add-custom-states-and-retrieve-custom-state-properties)
    for assemblies
  - Simple interface for
    [concretizing free parameters](#load-concrete-values-for-the-free-parameters-in-an-assembly)
    in a symbolic design
  - Symbolic parameters can auto-combine or concretize based on attachments (TODO)
  - Auto-generated and updated documentation upon GitHub commit


# Terminology and Conventions

Important terms used by the SymCAD library include:

  - **Part/Component/Shape**: Used interchangeably to refer to a single atomic shape that is
                              represented by an object extending the `SymPart` class, containing
                              its own set of physical geometric properties and placements
  - **Assembly**: A collection of parts along with their respective global placements and/or
                  attachments
  - **Attachment**: A physical, rigid joining of two parts (i.e., if one part moves or is rotated,
                    its attachments will also move or rotate)
  - **Connection**: A flexible or logical (non-physical) joining of two parts (i.e., if one part
                    moves, it does not affect its connections)
  - **Origin**: Used interchangebly with "Center of Rotation" or "Placement Center" to indicate
                the location on a part which serves as its center of placement as well as the
                point around which it rotates

Internal conventions assumed by the library are as follows:

  - **Coordinate systems**: All coordinate systems in this library are relative to their enclosed
                            parts and adhere to the following conventions: Each *x-axis* has its
                            origin at the front of a given part and extends positively toward the
                            rear. Each *y-axis* has its origin at the left of the part when looking
                            from the positive x-axis toward origin and extends positively to the
                            right. Each *z-axis* has its origin at the bottom of the part and
                            extends positively upward. The following images illustrate this, using
                            a UUV fairing as the basis:

  <p align="center">
    <img width="500" src="https://symbench.github.io/SymCAD/images/CoordinateSystem.png">
  </p>
  - **Local coordinate system**: The coordinate system used internally by each part to indicate
                                 the locations of its attachment and connection points, as well
                                 as its center of placement and rotation. All coordinates fall
                                 within the range `[0.0, 1.0]` and are relative to the total length
                                 (x-axis), width (y-axis), and height (z-axis) of the part. This
                                 coordinate system rotates along with the part.
  - **Global coordinate system**: The coordinate system used by an assembly to place and orient
                                  its constituent parts. It does not rotate, and its coordinates
                                  represent global placements in units of meters.
  - **Units**: Unless otherwise specified, all measurements are represented in base SI units (e.g.,
               meters, celcius, grams). Notable exceptions include mass (`kg`) and any measurements
               involving mass (e.g., density = `kg/m^3`).
  - **Orientation**: Refers to the final rotation of a part in the global coordinate system
                     according to the nautical and aviation convention of intrinsic, right-handed
                     rotations using the yaw-pitch-roll rotation order. This corresponds to first
                     rotating about the z-axis, followed by the y-axis, followed by the x-axis.
                     These angles are also called Tait-Bryan angles (related to Euler angles). For
                     convenience, any orientation may also be specified using a rotation matrix or
                     a quaternion.
  - **Yaw**: Refers to the rotation of a part around the *z-axis*. A positive yaw angle represents
             a counter-clockwise rotation when looking from the positive z-axis toward origin
             (i.e., a vehicle veering to the left from the point of view of a person inside
             the vehicle).
  - **Pitch**: Refers to the rotation of a part around the *y-axis*. A positive pitch angle
               represents a counter-clockwise rotation when looking from the positive y-axis toward
               origin (i.e., the nose of a vehicle pitching downward).
  - **Roll**: Refers to the rotation of a part around the *x-axis*. A positive roll angle
              represents a counter-clockwise rotation when looking from the positive x-axis toward
              origin (i.e., a vehicle tilting to the left from the point of view of a person
              inside the vehicle).

  <p align="center">
    <img width="550" src="https://symbench.github.io/SymCAD/images/RollPitchYaw.png">
  </p>
  - **Default orientation**: If not explicitly defined, the default orientation of a part will be
                             `(0, 0, 0)`, indicating no change from its default orientation.
  - **Default material density**: If not explicitly defined upon creation of a part, a material
                                  density of `1.0 kg/m^3` will be assumed (which may result in
                                  incorrect calculations for the mass of a part).
  - **Default origin**: Unless explicitly set, the default origin/center-of-rotation of a part
                        will be treated symbolically.
  - **Default placement**: Unless explicitly set, the default placement of a part will be treated
                           symbolically.
  - **Part geometry**: The geometric representation of each part is completely unique to the part
                       and is determined by either its `SymPart` class implementation or its
                       underlying CAD model, depending on how the part was created. In either case,
                       the `set_geometry()` method for a given part will always specify a set
                       of keywords indicating its precise underlying geometric properties.

Specific details regarding the geometric parameters and default orientation of any `SymCAD` part
can be found in its corresponding part-specific documentation page.


# Getting Started

To use the SymCAD library in your project, you may install it manually using the string
`git+https://github.com/SymBench/SymCAD.git` with `pip` or add it as a dependency in your
`requirements.txt` file. Alternately, you may add the GitHub repository as a submodule to your
project using `git submodule add https://github.com/SymBench/SymCAD`. If you plan to develop or
work on the SymCAD project itself, you should clone the
[SymCAD repository](https://github.com/SymBench/SymCAD) and install it using
`python3 -m pip install -e .` from the SymCAD root directory.

Once the library has been installed, you may begin work on your first SymCAD assembly as shown
in the following example:

```python
from symcad.core import Assembly
from symcad.parts import Pipe, FlangedFlatPlate, Torisphere

# Create random concrete components
front_endcap = FlangedFlatPlate('FrontEndcap')\\
   .set_geometry(radius_m=0.22, thickness_m=0.08)\\
   .set_orientation(roll_deg=0, pitch_deg=-90.0, yaw_deg=0)\\
   .add_attachment_point('EndcapAttachment', x=0.5, y=0.5, z=0)
center_pipe = Pipe('CenterPipe')\\
   .set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)\\
   .add_attachment_point('AttachmentFront', x=0.5, y=0.5, z=0)\\
   .add_attachment_point('AttachmentRear', x=0.5, y=0.5, z=1)
rear_endcap = Torisphere('RearEndcap')\\
   .set_geometry(base_radius_m=0.22, thickness_m=0.0025)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)\\
   .add_attachment_point('EndcapAttachment', x=0.5, y=0.5, z=0)

# Create assembly using attachments
assembly = Assembly('SymCadExample')
center_pipe.attach('AttachmentFront', front_endcap, 'EndcapAttachment')\\
           .attach('AttachmentRear', rear_endcap, 'EndcapAttachment')
assembly.add_part(front_endcap)
assembly.add_part(center_pipe)
assembly.add_part(rear_endcap)

# Globally place the front_endcap and export the CAD assembly
front_endcap.set_placement(placement=(0, 0, 0), local_origin=(0.5, 0.5, 1))
assembly.export('assembly_example.FCStd', 'freecad')
```

In the example just shown, a FreeCAD model is generated using parts with fully concrete geometries,
orientations, and placements. In many cases, these parameters may need to remain symbolic (e.g.,
creating a Pressure Vessel for an underwater vehicle where the material thickness of the part
depends on the maximum target vehicle depth, and its length may be depend on the number of
batteries being stored inside). In this case, these parameters may be kept symbolic by simply
*not* calling the respective `set_XXX` methods on the relevant part, or, if you must use these
methods (for example, to concretely set only *some* of the geometric parameters), you may keep
non-concrete parameters symbolic by passing them a value of `None`:

```python
from symcad.core import Assembly
from symcad.parts import Pipe, FlangedFlatPlate, Torisphere

# Create random concrete components with symbolic geometries
front_endcap = FlangedFlatPlate('FrontEndcap')\\
   .set_geometry(radius_m=None, thickness_m=0.08)\\
   .set_orientation(roll_deg=0, pitch_deg=-90.0, yaw_deg=0)\\
   .add_attachment_point('EndcapAttachment', x=0.5, y=0.5, z=0)
center_pipe = Pipe('CenterPipe')\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)\\
   .add_attachment_point('AttachmentFront', x=0.5, y=0.5, z=0)\\
   .add_attachment_point('AttachmentRear', x=0.5, y=0.5, z=1)
rear_endcap = Torisphere('RearEndcap')\\
   .set_geometry(base_radius_m=None, thickness_m=0.0025)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)\\
   .add_attachment_point('EndcapAttachment', x=0.5, y=0.5, z=0)

# Create assembly using attachments
assembly = Assembly('SymCadExample')
center_pipe.attach('AttachmentFront', front_endcap, 'EndcapAttachment')\\
           .attach('AttachmentRear', rear_endcap, 'EndcapAttachment')
assembly.add_part(front_endcap)
assembly.add_part(center_pipe)
assembly.add_part(rear_endcap)

# Globally place the front_endcap and and output the remaining free parameters
front_endcap.set_placement(placement=(0, 0, 0), local_origin=(0.5, 0.5, 1))
print('Free Parameters:', assembly.get_free_parameters())
```

This should print out the following list of symbolic free parameters:

```python
Free Parameters: ['CenterPipe_height', 'CenterPipe_radius', 'CenterPipe_thickness',
                  'FrontEndcap_radius', 'RearEndcap_base_radius']
```

Note that attempting to retrieve the physical properties of an assembly containing symbolic
parameters will return those properties as symbolic equations with respect to any remaining free
parameters, like so:

```python
print('Displaced Volume:', assembly.displaced_volume())
```

which should output a large equation with respect to the free parameters listed above. This is
useful when utilizing either a single part or an entire assembly to maintain some constraint; for
example, when using the [SymBench Constraint Solver](https://github.com/SymBench/constraint-prog)
to ensure that a Pressure Vessel has a large enough volume to contain the necessary number of
battery cells or to ensure that an assembly has coincident centers of buoyancy and gravity,
offset only by some z-axis value:

```python
# Create battery volume constraint
required_battery_cell_volume = 1.23  # Calculation done elsewhere
pressure_vessel.displaced_volume() >= required_battery_cell_volume

# Create center of gravity and buoyancy constraints
uuv_assembly.center_of_gravity().x == uuv_assembly.center_of_buoyancy().x
uuv_assembly.center_of_gravity().y == uuv_assembly.center_of_buoyancy().y
uuv_assembly.center_of_gravity().z <= uuv_assembly.center_of_buoyancy().z
```

To add to the utility of the above symbolic physical properties, it is also possible to specify
that an *external* symbol or equation should be used for any of the geometric, orientation, or
placement parameters of a part. For example, instead of making the entire geometry of the
previously shown Pressure Vessel *independently* symbolic, we could specify that its radius is
equal to a symbolic fairing radius, and its thickness is equal to some complex model-based
equation that depends on a target depth:

```python
# These symbols and equations could be defined elsewhere or retrieved
# from some other component or SymPart
fairing_radius = sympy.Symbol('fairing_radius_m')
maximum_depth = sympy.Symbol('maximum_depth_m')
material_thickness_model = ThicknessModel()  # Defined elsewhere
material_thickness = material_thickness_model.get_thickness_at(maximum_depth)

pressure_vessel.set_geometry(radius_m=fairing_radius, thickness_m=material_thickness)
```

The output of retrieving a physical property from the above Pressure Vessel would then be an
equation that depends (at least partially) on the maximum target vehicle depth and the total
fairing radius of the underwater vehicle.

Once concrete values have been determined for the available free parameters in an assembly, they
can be passed or loaded into that assembly using the following method to enable a fully defined
CAD model to be generated, along with its concretely defined physical properties:

```python
from symcad.core import Assembly
from symcad.parts import Sphere

# Define an assembly containing a single symbolic sphere
sphere = Sphere('RandomSphere')
assembly = Assembly('ExampleAssembly')
assembly.add_part(sphere)

# Create a dict of `free parameter: concrete value` pairs
#    These values should be solved for externally and loaded here
concrete_params = {
  'RandomSphere_origin_x': 0.5,
  'RandomSphere_origin_y': 0.5,
  'RandomSphere_origin_z': 0.5,
  'RandomSphere_placement_x': 0.1,
  'RandomSphere_placement_y': 0.0,
  'RandomSphere_placement_z': 0.0,
  'RandomSphere_radius': 0.2
}

# Generate the concrete assembly
concrete_assembly = assembly.make_concrete(concrete_params)

# Output some physical properties of the assembly using its model equations
print(concrete_assembly.displaced_volume())
print(concrete_assembly.center_of_gravity())

# Output the physical properties of the assembly as determined from its CAD model
print(concrete_assembly.get_cad_physical_properties())

# Export the CAD model as an STL file
concrete_assembly.export('concrete_test.stl', 'stl')
```

All of the previous examples show construction of a design using
[Assembly-by-Attachment](#create-an-assembly-using-assembly-by-attachment); however,
it is also possible to construct a concrete design using
[Assembly-by-Placement](#create-an-assembly-using-assembly-by-placement) which ignores the
entire attachment and connection subsystem of the library. In this mode of operation, you simply
create individual parts and opt *not* to call any of their `add_attachment_point()`, `attach()`,
`add_connection_port()`, or `connect()` methods:

```python
from symcad.core import Assembly
from symcad.parts import Pipe, FlangedFlatPlate, Torisphere

# Create random components
front_endcap = FlangedFlatPlate('FrontEndcap')\\
   .set_geometry(radius_m=0.22, thickness_m=0.08)\\
   .set_orientation(roll_deg=0, pitch_deg=-90.0, yaw_deg=0)
center_pipe = Pipe('CenterPipe')\\
   .set_geometry(radius_m=0.22, height_m=0.6, thickness_m=0.0025)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)
rear_endcap = Torisphere('RearEndcap')\\
   .set_geometry(base_radius_m=0.22, thickness_m=0.0025)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)

# Create an assembly without any attachments
assembly = Assembly('SymCadExample')
assembly.add_part(front_endcap)
assembly.add_part(center_pipe)
assembly.add_part(rear_endcap)

# Manually place all components in the assembly (or solve for them externally)
front_endcap.set_placement(placement=(0, 0, 0), local_origin=(0.5, 0.5, 1))
center_pipe.set_placement(placement=(0.08, 0, 0), local_origin=(0.5, 0.5, 0))
rear_endcap.set_placement(placement=(0.68, 0, 0), local_origin=(0.5, 0.5, 0))
assembly.export('assembly_by_placement_example.FCStd', 'freecad')
```

In this case, the placement of all parts will remain symbolic, and each part origin and
placement coordinate:

  - will appear as an additional free parameter in each physical property equation, and
  - can be concretized in exactly the same manner as the geometric properties shown above.

Of course, a hybrid approach may be taken whereby some parts are placed via Assembly-by-Attachment
and other parts are left to Assembly-by-Placement for the final concrete CAD representation.

Additional usage examples may be found in the [SymCAD Repository](https://github.com/SymBench/SymCAD)
under the `examples` directory.


# How do I ...

## ... create a new scripted SymCAD part?

A *scripted SymCAD part* is a part whose CAD representation is generated programmatically using
the [FreeCAD Python backend](https://www.freecadweb.org). A discussion of the FreeCAD API is
beyond the scope of this project, but many examples can be found online in the official
documentation or via search engine.

In order to create a part that uses this backend, you must simply create a Python class that
inherits from the `symcad.core.SymPart` class, and create a method in your class definition with the following
signature:

```python
@staticmethod
def your_method_name(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
```

where the `params` dictionary specifies the mapping between a symbolic geometric property in your
part and its desired concrete value, the `fully_displace` boolean specifies whether a
displacement model should be created, and a FreeCAD `Part.Solid` is returned. The contents of the
method are entirely up to you.

As an example, the following code is used to generate the CAD model for a paremetric 3D box:

```python
from PyFreeCAD.FreeCAD import FreeCAD, Part

@staticmethod
def __create_cad__(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
   thickness_mm = 1000.0 * params['thickness']
   outer_length_mm = 1000.0 * params['length']
   outer_width_mm = 1000.0 * params['width']
   outer_height_mm = 1000.0 * params['height']
   inner_length_mm = outer_length_mm - (2.0 * thickness_mm)
   inner_width_mm = outer_width_mm - (2.0 * thickness_mm)
   inner_height_mm = outer_height_mm - (2.0 * thickness_mm)
   outer = Part.makeBox(outer_length_mm, outer_width_mm, outer_height_mm)
   inner = Part.makeBox(inner_length_mm, inner_width_mm, inner_height_mm,
                        FreeCAD.Vector(thickness_mm, thickness_mm, thickness_mm))
   return outer if fully_displace else outer.cut(inner)
```

This method is passed to the `cad_model` parameter of the `__init__()` function of the
`symcad.core.SymPart` class from which your custom part must inherit:

```python
from PyFreeCAD.FreeCAD import FreeCAD, Part
from symcad.core.SymPart import SymPart
from sympy import Symbol, Expr

class MyCustomBox(SymPart):

   def __init__(self, identifier: str, material_density_kg_m3: float):
      super().__init__(identifier, self.__create_cad__, None, material_density_kg_m3)
      setattr(self.geometry, 'length', Symbol(self.name + '_length'))
      setattr(self.geometry, 'width', Symbol(self.name + '_width'))
      setattr(self.geometry, 'height', Symbol(self.name + '_height'))
      setattr(self.geometry, 'thickness', Symbol(self.name + '_thickness'))

   @staticmethod
   def __create_cad__(params: dict, fully_displace: bool) -> Part.Solid:
      thickness_mm = 1000.0 * params['thickness']
      outer_length_mm = 1000.0 * params['length']
      outer_width_mm = 1000.0 * params['width']
      outer_height_mm = 1000.0 * params['height']
      inner_length_mm = outer_length_mm - (2.0 * thickness_mm)
      inner_width_mm = outer_width_mm - (2.0 * thickness_mm)
      inner_height_mm = outer_height_mm - (2.0 * thickness_mm)
      outer = Part.makeBox(outer_length_mm, outer_width_mm, outer_height_mm)
      inner = Part.makeBox(inner_length_mm, inner_width_mm, inner_height_mm,
                           FreeCAD.Vector(thickness_mm, thickness_mm, thickness_mm))
      return outer if fully_displace else outer.cut(inner)
```

Additionally, your new SymCAD part class must implement the following abstract methods from the
`symcad.core.SymPart` parent class with the appropriate symbolic formulas for your new part:

```python
@property
def material_volume(self) -> Union[float, Expr]:

@property
def displaced_volume(self) -> Union[float, Expr]:

@property
def surface_area(self) -> Union[float, Expr]:

@property
def unoriented_center_of_gravity(self) -> Tuple[Union[float, Expr], Union[float, Expr], Union[float, Expr]]:

@property
def unoriented_center_of_buoyancy(self) -> Tuple[Union[float, Expr], Union[float, Expr], Union[float, Expr]]:

@property
def unoriented_length(self) -> Union[float, Expr]:

@property
def unoriented_width(self) -> Union[float, Expr]:

@property
def unoriented_height(self) -> Union[float, Expr]:
```

Finally, a `set_geometry(self, **kwargs)` method must be implemented by your custom SymCAD part
to set any symbolic parameters to their concrete values (or `None` if they should remain symbolic):

```python
def set_geometry(self, *, length_m: Union[float, None],
                          width_m: Union[float, None],
                          height_m: Union[float, None],
                          thickness_m: Union[float, None]) -> MyCustomBox:
   self.geometry.set(length=length_m, width=width_m, height=height_m, thickness=thickness_m)
   return self
```

For a full example of the custom 3D box just described, refer to `scripted_symcad_part.py` in the
`examples` directory of the [SymCAD Repository](https://github.com/SymBench/SymCAD).


## ... create a new modeled SymCAD part?

A *modeled SymCAD part* is a part whose CAD representation is pre-created by the user in the
FreeCAD format and stored in the `src/symcad/cadmodels/[X]` directory (where `X` is the directory
or directory tree to which the CAD model belongs).

Any type of CAD model internal structure is supported; however a number of conventions must be
satisfied:

  - The root label of the base part must be 'Model'
  - The root label of the displacement part (if it exists) must be 'DisplacedModel'
  - If the model is parameteric, the parameters must be stored in an internal spreadsheet with the
    label 'Parameters'
  - The first column of the 'Parameters' spreadsheet should be a description of the parameter, the
    second column should be the default value of the parameter (can be anything), and each value
    should have an alias assigned to it that is used by the CAD model to alter its geometry.
  - Any extra or derived non-public parameters should be specified in the spreadsheet underneath
    a row with a cell containing the word 'Derived' below all other public geometric parameters.

After creation and storage of the CAD model, its base file name is passed to the `cad_model`
parameter of the `__init__()` function of the `symcad.core.SymPart` class from which your custom
part must inherit. All other implementation details remain the same as described above for part
creation using a [scripted SymCAD approach](#create-a-new-scripted-symcad-part). Refer to the
`modeled_symcad_part.py` file under the `examples` directory of the
[SymCAD Repository](https://github.com/SymBench/SymCAD) for an example of a custom modeled
SymCAD part.


## ... import an existing CAD model?

An existing CAD model can be imported and used as a `SymPart` within SymCAD as if it were a
built-in part by using the `symcad.parts.generic.Custom` class. If the existing CAD model is in
the FreeCAD format and follows the rules outlined in the
[previous section](#create-a-new-modeled-symcad-part), the model can even be parametric and
contain symbolic free parameters. For example, to use an existing CAD model stored at
`/tmp/Existing.stp` as if it were a built-in `symcad.core.SymPart`, you can use any of the
following templates:

```python
from symcad.parts import Custom

custom_shape = Custom('Custom', 'Shape', '/tmp/Existing.stp')
custom_shape_with_neural_net = Custom('Custom', 'ShapeWithNN', '/tmp/Existing.stp', '/tmp/ExistingNN.tar.xz')
custom_shape_with_density = Custom('Custom', 'ShapeWithDensity', '/tmp/Existing.stp', None, 1028.0)
```

The `symcad.parts.generic.Custom` SymPart class can also be used to create a custom part based on
a scripted CAD representation. This is achieved by passing a static CAD creation method to the
`symcad.parts.generic.Custom` initializer as described in the
[scripted SymCAD section](#create-a-new-scripted-symcad-part):

```python
from PyFreeCAD.FreeCAD import FreeCAD, Part
from symcad.parts import Custom

def cad_creation_method(params: dict, fully_displace: bool) -> Part.Solid:
   # Your implementation here

custom_shape = Custom('Custom', 'Shape', cad_creation_method)
```

Once created, an imported `Custom` part behaves exactly the same as any other `SymPart` in the
library.

Note, if an existing **parametric** CAD model is imported but no corresponding neural network is
specified to represent a mapping between the geometric parameters of the part and its
mass/physical properties, a neural network will automatically be trained to learn these mappings
unless a value of `False` is passed to the `auto_train_missing_property_model` parameter of the
`symcad.parts.generic.Custom` constructor. This operation can take quite some time, so it is
recommended that this be done when you are not expecting to continue working with SymCAD for
awhile. Once trained, the neural network will be stored for later retrieval so that the training
process does not have to be repeated again in the future.


## ... retrieve physical properties from a part?

The following list of physical properties may be retrieved from a SymCAD part at any time by
simply requesting the property method on the corresponding part:

  - mass
  - material volume
  - displaced volume
  - surface area
  - unoriented center of gravity
  - oriented center of gravity
  - unoriented center of buoyancy
  - oriented center of buoyancy
  - unoriented length
  - oriented length
  - unoriented width
  - oriented width
  - unoriented height
  - oriented height

```python
# Example of accessing some physical properties for a part
print('Displaced Volume:', part.displaced_volume)
print('Center of Gravity (Unoriented):', part.unoriented_center_of_gravity)
```

For properties that contain both an `oriented` and an `unoriented` version, the `unoriented`
version will return the corresponding property as if the part were created with an orientation
of 0\u00B0 yaw, 0\u00B0 pitch, and 0\u00B0 roll. The `oriented` version will return the
corresponding property using the orientation of the underlying part as specified by the user
(even if that orientation is symbolic).


## ... create an assembly using Assembly-by-Placement?

Assembly-by-Placement is used to allow for complete control over the precise placement and
orientation of every part within an assembly (represented by the `symcad.core.Assembly` class).
This mode is the default for all SymPart components for which none of the
`add_attachment_point()`, `attach()`, `add_connection_port()`, or `connect()` methods have
been called. In this case, the placement of a part will be represented by three symbolic
parameters representing the origin/center-of-placement of the part in its own coordinate
space, as well as three additional symbolic coordinates representing the placement of the
origin of the part in the global coordinate space.

The coordinates for the origin of the part are expected to fall in the range `[0.0, 1.0]` and
are relative to the x-axis length, y-axis width, and z-axis height of the part. The coordinates
for the global placement of the part are absolute measurements in units of meters. If one or
more of these parameters should be set to a concrete value while the other parameters remain
symbolic, the `set_placement()` method may be called with a value of `None` for all parameters
which are intended to remain symbolic:

```python
concrete_part.set_placement(placement=(None, 0, 0), local_origin=(0.5, 0.5, None))
```

In this example, the local origin of the part will be placed halfway along its x- and y-axis, while
its z-component will remain symbolic. Likewise, the x-placement of the part will be symbolic,
while the y- and z-coordinates of the placement will be set to 0, as can be seen when printing
the free parameters of an assembly containing this part:

```python
# Partially place a concrete part in an assembly
concrete_part = Sphere('TestSphere').set_geometry(radius_m=1.0)
concrete_part.set_placement(placement=(None, 0, 0), local_origin=(0.5, 0.5, None))
assembly.add_part(concrete_part)
print('Free Parameters:', assembly.get_free_parameters())

# Output should be:
# Free Parameters: ['TestSphere_origin_z', 'TestSphere_placement_x']
```

In summary, to utilize Assembly-by-Placement, simply call the `add_part()` method of a
`symcad.core.Assembly` to add all parts that have been placed using their respective
`set_placement()` methods (or not placed at all, in which case, the placements will be
symbolic):

```python
from symcad.core import Assembly
from symcad.parts import Cuboid, Cylinder, Sphere

# Create random components
box = Cuboid('RandomBox')\\
   .set_geometry(length_m=0.12, width_m=0.08, height_m=0.22)
cylinder = Cylinder('RandomCylinder')\\
   .set_geometry(radius_m=0.22, height_m=0.6)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)
sphere = Sphere('RandomSphere')\\
   .set_geometry(radius_m=0.20)

# Manually place all components in the assembly
box.set_placement(placement=(0, 0, 0), local_origin=(0, 0.5, 0.5))
cylinder.set_placement(placement=(0.12, 0, 0), local_origin=(0.5, 0.5, 0))
sphere.set_placement(placement=(0.72, 0, 0), local_origin=(0, 0.5, 0.5))

# Create and export an Assembly-by-Placement
assembly = Assembly('AssemblyByPlacement')
assembly.add_part(box)
assembly.add_part(cylinder)
assembly.add_part(sphere)
assembly.export('assembly_by_placement_example.FCStd', 'freecad')
```


## ... create an assembly using Assembly-by-Attachment?

Assembly-by-Attachment is used to automate the process of placing rigidly attached parts within a
`symcad.core.Assembly`. Using this placement method, the intricacies of part placement can be
relegated to the SymCAD library which may greatly simplify the number of free variables in the
resulting symbolic assembly.

In order to use this methodology, individual `SymPart` components must define one or more
*attachment points* using the `add_attachment_point()` method, which defines a point in the local
coordinate system of the part that can rigidly attach to other parts:

```python
from symcad.core import Assembly
from symcad.parts import Cuboid, Cylinder, Sphere

# Create random components
box = Cuboid('RandomBox')\\
   .set_geometry(length_m=0.12, width_m=0.08, height_m=0.22)\\
   .add_attachment_point('BoxAttachment', x=1.0, y=0.5, z=0.5)
cylinder = Cylinder('RandomCylinder')\\
   .set_geometry(radius_m=0.22, height_m=0.6)\\
   .set_orientation(roll_deg=0, pitch_deg=90.0, yaw_deg=0)\\
   .add_attachment_point('FrontAttachment', x=0.5, y=0.5, z=0)\\
   .add_attachment_point('RearAttachment', x=0.5, y=0.5, z=1)
sphere = Sphere('RandomSphere')\\
   .set_geometry(radius_m=0.20)\\
   .add_attachment_point('SphereAttachment', x=0, y=0.5, z=0.5)

# Create an Assembly-by-Attachment
assembly = Assembly('AssemblyByAttachment')
cylinder.attach('FrontAttachment', box, 'BoxAttachment')\\
        .attach('RearAttachment', sphere, 'SphereAttachment')
assembly.add_part(box)
assembly.add_part(cylinder)
assembly.add_part(sphere)

# Globally place the box and and export the assembly
box.set_placement(placement=(0, 0, 0), local_origin=(0, 0.5, 0.5))
assembly.export('assembly_by_attachment_example.FCStd', 'freecad')
```

Note that when using Assembly-by-Attachment, there is no need to call the `set_placement()` method
of a `SymPart` since its placement will be defined by the rigid attachments it makes to other
parts. The `set_placement()` method **should** be called on one single part, however, in order to
globally place the entire assembly at a known location. Also note that a mixture of
Assembly-by-Placement and Assembly-by-Attachment can be used to fully define the internal structure
of an assembly.


## ... retrieve physical properties from an assembly?

The physical properties of a composite assembly can be retrieved in much the same way as the
individual properties of a `SymPart`, namely by calling a method corresponding to the desired
physical property on an instance of the `symcad.core.Assembly` being examined.

The available properties for an assembly include:
  - mass
  - material volume
  - displaced volume
  - surface_area
  - center of gravity
  - center of buoyancy
  - length
  - width
  - height.

Note that there is no differentiation between `oriented` and `unoriented` properties for an
assembly, since this is a mostly useless distinction when examining cumulative properties:

```python
# Example of accessing some physical properties of an assembly
print('Displaced Volume: assembly.displaced_volume())
print('Center of Gravity: assembly.center_of_gravity())
```


## ... access properties of subsets of parts in an Assembly?

Once created, it may be necessary to obtain the physical or geometric properties of only a subset
of the parts contained within an assembly. In order to achieve this, parts can be grouped into
so-called *collections* when added to a `symcad.core.Assembly` using the `add_part()` method. This
method has the following signature, where the optional `include_in_collections` parameter may be
used to specify a list of collection names to which the part should be added:

```python
def add_part(self, shape: SymPart, include_in_collections: List[str] = [])
```

Once added to one or more collections, the geometric properties of the `SymPart` components
contained in any number of those collections may be accessed by specifying the collections of
interest in the corresponding property accessor of the `symcad.core.Assembly` object. For example,
to identify the center of gravity of a collection of green balls within an assembly containing
both green and blue balls, the following may be carried out:

```python
from symcad.core import Assembly
from symcad.parts import Sphere

# Add a number of blue and green balls to an assembly
assembly = Assembly('BallContainer')
for idx in range(10):
   blue_ball = Sphere('BlueBall' + str(idx))
   green_ball = Sphere('GreenBall' + str(idx))
   assembly.add_part(blue_ball.set_geometry(radius_m=0.1), ['blue_balls'])
   assembly.add_part(green_ball.set_geometry(radius_m=0.1), ['green_balls'])

# Retrieve the center of gravity of only the green balls
print(assembly.center_of_gravity(['green_balls']))
```


## ... load concrete values for the free parameters in an assembly?

Once created, a SymCAD assembly will likely contain a number of free parameters that must be
solved for externally. A list of these free parameters can be retrieved at any time by calling
the `get_free_parameters()` method on a `symcad.core.Assembly` object. In order to load concrete
values back into an assembly, the `make_concrete(params)` method may be used:

```python
from symcad.core import Assembly
from symcad.parts import Sphere

# Define an assembly containing a single symbolic sphere
sphere = Sphere('RandomSphere')
assembly = Assembly('ExampleAssembly')
assembly.add_part(sphere)

# Create a dict of `free parameter: concrete value` pairs
concrete_params = {
  'RandomSphere_origin_x': 0.5,
  'RandomSphere_origin_y': 0.5,
  'RandomSphere_origin_z': 0.5,
  'RandomSphere_placement_x': 0.1,
  'RandomSphere_placement_y': 0.0,
  'RandomSphere_placement_z': 0.0,
  'RandomSphere_radius': 0.2
}

# Generate the concrete assembly
concrete_assembly = assembly.make_concrete(concrete_params)
```

Note that this method returns a *copy* of the assembly with as many concrete parameters filled in
as possible, but the original assembly object remains unaltered.


## ... detect part interferences within an Assembly?

Once a concrete assembly has been created, it is possible to check for part interferences by
calling the `check_interferences()` method on the assembly object:

```python
from symcad.core import Assembly
from symcad.parts import Sphere

# Create two random spheres
sphere1 = Sphere('Sphere1').set_geometry(radius_m=0.1)
sphere2 = Sphere('Sphere2').set_geometry(radius_m=0.1)

# Add the spheres to an assembly and place them so that they overlap
assembly = Assembly('InterferenceAssembly')
assembly.add_part(sphere1)
assembly.add_part(sphere2)
sphere1.set_placement(placement=(0, 0, 0), local_origin=(0.5, 0.5, 0.5))
sphere2.set_placement(placement=(0.1, 0, 0), local_origin=(0.5, 0.5, 0.5))

# Output the result of an interference check
print('The following parts interference: {}'.format(assembly.check_interferences()))
# Should output: [('Sphere1', 'Sphere2')]
```

This will return a list of pairs, where each pair indicates two `SymPart` objects within the
assembly that interfere with one another. Note that if your assembly contains any symbolic
parameters or placements, you must first create a concrete version by calling
`assembly.make_concrete(params)` or this method will raise a runtime exception.


## ... export a CAD model into a specific format?

Both individual SymCAD parts (any part derived from `symcad.core.SymPart`) and full SymCAD
assemblies can be exported to the 'FreeCAD', 'STEP', or 'STL' CAD formats. This is done by
calling the `export()` method on the part or assembly of interest:

```python
from symcad.core import Assembly
from symcad.parts import Cylinder, Sphere

# Create random parts
assembly = Assembly('ExampleExport')
cylinder = Cylinder('RandomCylinder')\\
   .set_geometry(radius_m=1, height_m=2)\\
   .set_placement(placement=(0, 0, 0), local_origin=(0, 0, 0))
sphere = Sphere('RandomSphere')\\
   .set_geometry(radius_m=1)\\
   .set_placement(placement=(0, 0, 2), local_origin=(0, 0, 0))

# Export the parts to various formats
sphere.export('sphere.FCStd', 'freecad')
cylinder.export('cylinder.stl', 'stl')

# Export an assembly containing all parts
assembly.add_part(sphere)
assembly.add_part(cylinder)
assembly.export('assembly.stp', 'step')
```

Note that if your assembly contains any symbolic parameters or placements, you must first create
a concrete version by calling `assembly.make_concrete(params)` and then call `export()` on the
resulting concrete assembly object. This may also be necessary even if your assembly contains only
concrete geometric parameters but was constructed via
[Assembly-by-Attachment](#create-an-assembly-using-assembly-by-attachment).


## ... add custom states and retrieve custom-state properties?

Custom states are useful for manipulating parts and assemblies with moveable components or
multiple geometric configurations. Essentially, a `SymPart` is able to define its own set of
custom states that can be used to alter its CAD representation or its set of symbolic properties.
For example, a *Pitch Control* part may have three internal custom states corresponding to the
configurations necessary to achieve its minimum, maximum, and neutral pitch angles.

In order to add custom states to a `SymPart`, the part should implement the
`get_valid_states()` method from the `symcad.core.SymPart` class to return a list of strings
corresponding to all valid states that the part is able to be configured for. To configure
a part for a specific state, the `set_state()` method should be called on the part object.
Note that this method takes a *list* of state names, making it possible to configure a
`SymPart` for multiple states at the same time (e.g., minimum pitch and neutral roll).

Since it is possible that several parts may share the same custom state name, it is easy to set
all parts in an assembly to the same configuration by calling the
`set_state(state_names: Union[List[str], None])` method on the assembly object itself. If a part
within the assembly does not recognize a state listed in the `state_names` parameter, that part
will simply ignore it. Note that `state_names` may contain any number of states for which to
configure the assembly. An example of a part and assembly that utilizes custom states can be
found in `custom_states.py` in the `examples` directory of the
[SymCAD Repository](https://github.com/SymBench/SymCAD).


## ... create a design using the JSON Graph API?

A programmatically manipulated SymCAD assembly can be stored as a JSON Graph file using the
`save(file_name)` method directly from the assembly instance itself. Likewise a stored JSON
Graph assembly can be loaded using the static `Assembly.load(file_name)` method:

```python
assembly = Assembly('SymCadAssembly')  # Defined and manipulated elsewhere

# Store the assembly as a JSON graph file
assembly.save('assembly_file.json')

# Re-load the assembly from a JSON graph file
assembly = Assembly.load('assembly_file.json')
```

A sample JSON Graph file can be found in the `tests/core/test_json_graph.json` file in the
[SymCAD Repository](https://github.com/SymBench/SymCAD). In general, it contains four top-level
keys: `name`, `parts`, `attachments`, and `connections`. The `name` is simply the
user-specified name for the assembly, and `attachments` and `connections` are both lists of
dictionaries containing keys specifying the source and destination SymCAD parts and attachment
port names. The `parts` item is the most complicated and contains a list of dictionaries,
each of which fully specifies a unique SymCAD part in the assembly. Its fields are as follows:

  - `name`: Unique identifying part name
  - `type`: String representing the underlying part type as laid out in the SymCAD `parts` tree
            (e.g., 'generic.Capsule')
  - `geometry`: Dictionary containing keys representing the unique geometry for the given
                SymCAD part type. Concrete values are specified as floating point numbers, while
                symbolic values are specified as strings
  - `material_density`: Uniform material density of the part in `kg/m^3`
  - `placement_point`: Dictionary containing the center of placement of the part (as a percentage
                       of its x-length, y-width, and z-height in the range `[0.0, 1.0]`)
  - `attachment_points`: List of dictionaries, each containing the location of an attachment point
                         on the part (as a percentage of its x-length, y-width, and z-height in the
                         range `[0.0, 1.0]`)
  - `connection_ports`: List of dictionaries, each containing the location of a connection port
                        on the part (as a percentage of its x-length, y-width, and z-height in the
                        range `[0.0, 1.0]`)
  - `orientation`: Dictionary containing the roll, pitch, and yaw angles of the part in degrees.
                   Concrete values are specified as floating point numbers, while symbolic values
                   are specified as strings
  - `static_placement`: Dictionary containing the global XYZ coordinates of the part's center of
                        placement, or `None` if the part is not statically placed. Concrete values
                        are specified as floating point numbers, while symbolic values are
                        specified as strings
  - `is_exposed`: Boolean indicating whether the part is exposed to its surrounding environment


## ... train a neural network to represent the physical properties of a SymPart?

The easiest way to train a neural network to represent the physical properties of a `SymPart`
depends on how the part was created. If a fully custom `symcad.core.SymPart` was created, you
should simply ensure that the `SymPart` initializer (`super().__init__`) is called with an
appropriate storage path for the neural network:

```python
class NewShape(SymPart):
   def __init__(self, identifier: str, material_density_kg_m3: float) -> None:
      super().__init__(identifier, 'path_to_cad_file.FCStd', 'path_to_neural_net.tar.xz', material_density_kg_m3)
```

Note that the neural network path should always be in the `*.tar.xz` format. If the neural net
does not exist, it will be trained and stored the first time the new `SymPart` is created, without
any intervention required on the part of the user.

If the part is created through the `symcad.parts.generic.Custom` interface, simply ensure that
the `pretrained_geometric_properties_model` initializer parameter is set to an appropriate storage
path:

```python
new_part = Custom('PartType', 'PartID', creation_callback, 'PartType.tar.xz')
```

As above, the network will automatically be trained the first time the `Custom` part is created.

There is also an advanced method to train the neural network for a given `SymPart` which should
be used if you only need to learn a subset of the possible physical properties for a part
(such as only learning the z-component of the center of gravity). Using this method involves
creating an instance of your custom part **without** specifying a path to its neural network,
and using this instance to manually train the network for the properties of interest:

```python
from symcad.core.ML import NeuralNetTrainer
from symcad.parts import Custom

# Specify your new custom part and the desired filename for its network
new_part = Custom('CustomType', 'TrainingPart', creation_callback)
neural_net_filename = 'custom_type.tar.xz'

# Create a trainer to learn the physical properties of interest
trainer = NeuralNetTrainer(new_part, ['material_volume', 'cg_z'])
trainer.learn_parameters(32)
trainer.save(neural_net_filename)
```

In the above example, the list of physical properties that are available for the neural network
to learn is the same as the list of properties retrievable from the underlying CAD model:

  - Lengths: `xlen`, `ylen`, `zlen`
  - Centers of Gravity: `cg_x`, `cg_y`, `cg_z`
  - Centers of Buoyancy: `cb_x`, `cb_y`, `cb_z`
  - Volume and Area: `material_volume`, `displaced_volume`, `surface_area`

The `learn_parameters` method expects a batch size to be passed in as a parameter. If you unsure
of what value to use, `32` seems to work well.

Once training has completed, you should move the stored neural network to an appropriate location,
and it can then be specified in the constructor of your new part for future use.


# API Documentation

Module- and class-specific API documentation can be accessed using the links in the navigation
frame to the left underneath the `Submodules` heading. Especially important are the part-specific
documentation pages that specify the geometric properties and orientation defaults for each part
currently present in the library. For example, specific information about the generic `Cone` part
can be accessed under the `symcad.parts.generic.Cone` documentation page.


# Issues

If you encounter any issues or have suggestions for additional functionality, please utilize the
[SymCAD Issues](https://github.com/SymBench/SymCAD/issues) page to open a new ticket.
"""

__version__ = '1.0.0'
__author__ = 'Will Hedgecock'
__credits__ = 'Vanderbilt University'
__docformat__ = 'markdown'
