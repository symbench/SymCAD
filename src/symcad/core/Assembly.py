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
from PyFreeCAD.FreeCAD import FreeCAD
from .Coordinate import Coordinate
from .SymPart import SymPart
from .CAD import CadGeneral
from typing import Any, Dict, List, Literal
from typing import Optional, Set, Union
from sympy import Min, Max
from pathlib import Path

def _isfloat(num: Any) -> bool:
   """Private helper function to test if a value is float-convertible."""
   try:
      float(num)
      return True
   except Exception:
      return False


class Assembly(object):
   """Class representing an assembly of individual `SymPart` parts.

   Parts can be added to an assembly using the `add_part()` method and may include
   placements or orientations that are symbolic; however, an assembly cannot be exported to a
   CAD model until all parameters have been set to concrete values, either directly within
   each assembled part, or by passing a dictionary of `key: value` pairs to the `export`
   method for each symbolic parameter within the model.
   """

   # Public attributes ----------------------------------------------------------------------------

   name: str
   """Unique identifying name for the `Assembly`."""

   parts: List[SymPart]
   """List of `SymPart` parts within the assembly."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, assembly_name: str) -> None:
      """Initializes an `Assembly` object with the specified `assembly_name`."""
      self.name = assembly_name
      self.parts = []


   # Built-in method implementations --------------------------------------------------------------

   def __eq__(self, other: Assembly) -> bool:
      is_equal = False
      for part in self.parts:
         for part2 in other.parts:
            if part.name == part2.name and part == part2:
               is_equal = True
      return self.name == other.name and is_equal


   # Private helper methods -----------------------------------------------------------------------

   def _make_concrete(self, params: Dict[str, float]) -> None:
      """Concretizes as many symbolic parameters as possible given the `key: value` pairs
      in `params`."""
      for part in self.parts:
         if part.static_placement is None:
            part.static_placement = Coordinate(part.name + '_placement')
         if part.static_origin is None:
            part.static_origin = Coordinate(part.name + '_origin')
         for point in part.attachment_points:
            for key, val in [(k, v) for k, v in point.__dict__.items() if k != 'name']:
               if not _isfloat(val) and str(val) in params:
                  setattr(point, key, params[str(val)])
         for point in part.connection_ports:
            for key, val in [(k, v) for k, v in point.__dict__.items() if k != 'name']:
               if not _isfloat(val) and str(val) in params:
                  setattr(point, key, params[str(val)])
         for key, val in [(k, v) for k, v in part.geometry.__dict__.items() if k != 'name']:
            if not _isfloat(val) and str(val) in params:
               setattr(part.geometry, key, params[str(val)])
         for key, val in [(k, v) for k, v in part.orientation.__dict__.items() if k != 'name']:
            if not _isfloat(val) and str(val) in params:
               setattr(part.orientation, key, params[str(val)])
         for key, val in \
             [(k, v) for k, v in part.static_origin.__dict__.items() if k != 'name']:
            if not _isfloat(val) and str(val) in params:
               setattr(part.static_origin, key, params[str(val)])
         for key, val in \
             [(k, v) for k, v in part.static_placement.__dict__.items() if k != 'name']:
            if not _isfloat(val) and str(val) in params:
               setattr(part.static_placement, key, params[str(val)])


   @staticmethod
   def _verify_fully_concrete(part: SymPart, raise_error_if_symbolic: bool) -> Set[str]:
      """Ensures that the placement, origin, geometry, and orientation of the specified part
      all have concrete values."""
      free_parameters = set()
      for key, val in part.static_origin.__dict__.items():
         if key != 'name' and not _isfloat(val):
            free_parameters.update([str(symbol) for symbol in val.free_symbols])
      for key, val in part.static_placement.__dict__.items():
         if key != 'name' and not _isfloat(val):
            free_parameters.update([str(symbol) for symbol in val.free_symbols])
      for key, val in part.orientation.__dict__.items():
         if key != 'name' and not _isfloat(val):
            free_parameters.update([str(symbol) for symbol in val.free_symbols])
      for key, val in part.geometry.__dict__.items():
         if key != 'name' and not _isfloat(val):
            free_parameters.update([str(symbol) for symbol in val.free_symbols])
      if free_parameters and raise_error_if_symbolic:
         raise RuntimeError('Symbolic parameters still remain in the assembly: {}'
                            .format(free_parameters))
      return free_parameters


   def _collect_unique_assemblies(self) -> List[List[SymPart]]:
      """Creates a collection of unique assemblies by identifying all parts which rigidly attach
      to form a single contiguous sub-assembly."""
      assemblies = []
      remaining_parts = [part.name for part in self.parts]
      for part in self.parts:
         if part.name in remaining_parts:
            assembly = []
            self._collect_unique_assembly(assembly, part, remaining_parts)
            assemblies.append(assembly)
      return assemblies


   def _collect_unique_assembly(self, assembly: List[SymPart],
                                      root_part: SymPart,
                                      remaining_parts: List[str]) -> None:
      """Recursively adds rigidly attached parts to the current unique assembly of parts."""
      if root_part.name in remaining_parts:
         assembly.append(root_part)
         remaining_parts.remove(root_part.name)
         for attachment_name in root_part.attachments.values():
            attached_part_name = attachment_name.split('#')[0]
            attached_part = [part for part in self.parts if part.name == attached_part_name]
            if not attached_part:
               raise RuntimeError('A SymPart attachment ({}) to "{}" is not present in the '
                                    'current assembly'.format(attached_part_name, root_part.name))
            self._collect_unique_assembly(assembly, attached_part[0], remaining_parts)


   @staticmethod
   def _find_best_root_part(assembly: List[SymPart]) -> SymPart:
      """Searches for the part in the assembly with the greatest number of concrete placement
      parameters."""
      best_part = None
      most_concrete = -1
      for part in assembly:
         num_concrete = sum([1 for key, val in part.static_origin.__dict__.items()
                             if key != 'name' and _isfloat(val)]) + \
                        sum([1 for key, val in part.static_placement.__dict__.items()
                             if key != 'name' and _isfloat(val)]) \
                        if part.static_placement is not None else 0
         if num_concrete > most_concrete:
            most_concrete = num_concrete
            best_part = part
      for part in assembly:
         if part.name != best_part.name:
            part.static_origin = part.static_placement = None
      return best_part


   def _place_parts(self) -> None:
      """Updates the global placement of all assembled parts based on their rigid attachments
      to other parts.
      """
      for assembly in self._collect_unique_assemblies():
         root_part = Assembly._find_best_root_part(assembly)
         if root_part.static_placement is None:
            root_part.set_placement(placement=(None, None, None), local_origin=(None, None, None))
         self._solve_rigid_placements(None, root_part)


   def _solve_rigid_placements(self, previous_part: Union[SymPart, None],
                                     current_part: SymPart) -> None:
      """Recursively updates the global placement of all parts rigidly attached to the
      current part.

      Parameters
      ----------
      previous_part : `Union[SymPart, None]`
         The previous part in the assembly chain or `None` if this is the first part whose
         attachments are being placed.
      current_part : `SymPart`
         The part whose attachments are being placed.
      """

      # Iterate through all attachments to the current part
      for local_name, remote_name in current_part.attachments.items():

         # Search for the remotely attached part
         remote_part_name, remote_attachment_name = remote_name.split('#')
         remote_part = [part for part in self.parts if part.name == remote_part_name]
         if not remote_part:
            raise RuntimeError('A SymPart attachment ({}) to "{}" is not present in the current '
                               'assembly'.format(remote_part_name, current_part.name))
         remote_part = remote_part[0]
         remote_attachment_point = [point for point in remote_part.attachment_points
                                    if point.name == remote_attachment_name]
         if not remote_attachment_point:
            raise RuntimeError('The remote attachment point "{}" does not exist on the remote '
                               'part "{}"'.format(remote_attachment_name, remote_part.name))

         # Calculate the placement of the remotely attached part if not already placed
         for local_attachment_point in current_part.attachment_points:
            if local_attachment_point.name == local_name and \
               not (previous_part and previous_part.name == remote_part_name):

               # Compute the center of placement of the attachment in the global coordinate space
               current_origin = current_part.static_origin
               current_placement = current_part.static_placement
               center_of_placement = Coordinate('Placement',
                     x = current_placement.x + ((local_attachment_point.x - current_origin.x)
                                                * current_part.unoriented_length),
                     y = current_placement.y + ((local_attachment_point.y - current_origin.y)
                                                * current_part.unoriented_width),
                     z = current_placement.z + ((local_attachment_point.z - current_origin.z)
                                                * current_part.unoriented_height))
               rotated_x, rotated_y, rotated_z = \
                  current_part.orientation.rotate_point(current_placement.as_tuple(),
                                                        center_of_placement.as_tuple())

               # Update the placement of the attached part and continue solving
               if remote_part.static_placement is None:
                  remote_part.static_origin = remote_attachment_point[0].clone()
                  remote_part.static_placement = Coordinate(remote_part.name + '_placement',
                                                            x=rotated_x, y=rotated_y, z=rotated_z)
                  self._solve_rigid_placements(current_part, remote_part)
               else:
                  # TODO: Something here to add an additional constraint for solving for unknowns
                  pass


   # Public methods -------------------------------------------------------------------------------

   def clone(self) -> Assembly:
      """Returns an exact clone of this `Assembly` instance."""
      cloned = Assembly(self.name)
      for part in self.parts:
         cloned.parts.append(part.clone())
      return cloned


   def add_part(self, shape: SymPart) -> None:
      """Adds a `SymPart` to the current assembly.

      Every part within an assembly must have a unique name or this method will fail with a
      `KeyError`.

      Parameters
      ----------
      shape : `SymPart`
         part to add to the assembly.

      Raises
      ------
      `KeyError`
         If a part within the assembly contains the same name as the part being added.
      """
      for part in self.parts:
         if part.name == shape.name:
            raise KeyError('A part with the name "{}" already exists in this assembly'
                           .format(shape.name))
      self.parts.append(shape)


   def get_free_parameters(self) -> List[str]:
      """Returns a list of all free parameters present inside the assembly."""
      free_parameters = set()
      assembly = self.clone()
      assembly._place_parts()
      for part in assembly.parts:
         free_parameters.update(assembly._verify_fully_concrete(part, False))
      return sorted(free_parameters)


   def make_concrete(self, params: Optional[Dict[str, float]] = None) -> Assembly:
      """
      Creates a copy of the current `Assembly` with all free parameters set to their concrete
      values as specified in the `params` parameter.

      Parameters
      ----------
      params : `Dict[str, float]`, optional, default=None
         Dictionary of free variables along with their desired concrete values.

      Returns
      -------
      `Assembly`
         A copy of the current Assembly containing as many concrete parameters and
         placements as possible.
      """
      concrete_assembly = self.clone()
      concrete_assembly._make_concrete([] if params is None else params)
      concrete_assembly._place_parts()
      return concrete_assembly


   def export(self, file_save_path: str,
                    model_type: Literal['freecad', 'step', 'stl'],
                    create_displacement_model: Optional[bool] = False) -> None:
      """Exports the current assembly as a CAD file.

      Note that all parameters in the assembly must be concrete with no free variables remaining.
      This can be achieved by first calling `make_concrete(params)` on the assembly object and
      then calling `export()` on the resulting concrete assembly.

      If any free parameter is missing a corresponding concrete value in the `params`
      dictionary, this method will raise a `RuntimeError`.

      Parameters
      ----------
      file_save_path : `str`
         Relative or absolute path of the desired output file.
      model_type : {'freecad', 'step', 'stl'}
         Desired format of the exported CAD model.
      create_displacement_model : `bool`, optional, default=False
         Whether to create a model representing total environmental displacement.

      Raises
      ------
      `RuntimeError`
         If a free parameter within the assembly does not contain a corresponding concrete value.
      """

      # Create any necessary path directories
      file_path = Path(file_save_path).absolute().resolve()
      if not file_path.parent.exists():
         file_path.parent.mkdir()

      # Create a new assembly document and add all concrete CAD parts to it
      assembly = self.clone()
      assembly._place_parts()
      doc = FreeCAD.newDocument(self.name)
      for part in assembly.parts:
         Assembly._verify_fully_concrete(part, True)
         part.__cad__.add_to_assembly(part.name,
                                      doc,
                                      part.geometry.__dict__,
                                      part.static_origin.as_tuple(),
                                      part.static_placement.as_tuple(),
                                      part.orientation.as_tuple(),
                                      create_displacement_model)

      # Recompute and create the requested version of the model
      doc.recompute()
      CadGeneral.save_assembly(file_path, model_type, doc)
      FreeCAD.closeDocument(doc.Name)


   def get_cad_physical_properties(self) -> Dict[str, float]:
      """Returns all physical properties of the Assembly as reported by the underlying CAD model.

      Returns
      -------
      `Dict[str, float]`
         A dictionary containing all physical properties of the underlying CAD model.
      """

      # Create an assembly document and iterate through all CAD parts
      material_densities = {}
      assembly = self.clone()
      assembly._place_parts()
      doc = FreeCAD.newDocument(self.name)
      displacement_doc = FreeCAD.newDocument(self.name + '_displacement')
      for part in assembly.parts:

         # Ensure that the part is fully concrete, and add it to the current assembly
         Assembly._verify_fully_concrete(part, True)
         material_densities[part.name] = part.material_density
         part.__cad__.add_to_assembly(part.name,
                                      doc,
                                      part.geometry.__dict__,
                                      part.static_origin.as_tuple(),
                                      part.static_placement.as_tuple(),
                                      part.orientation.as_tuple(),
                                      False)
         if part.is_exposed:
            part.__cad__.add_to_assembly(part.name,
                                       displacement_doc,
                                       part.geometry.__dict__,
                                       part.static_origin.as_tuple(),
                                       part.static_placement.as_tuple(),
                                       part.orientation.as_tuple(),
                                       True)

      # Recompute and calculate the physical properties of the resulting model
      doc.recompute()
      displacement_doc.recompute()
      physical_properties = CadGeneral.fetch_assembly_physical_properties(doc,
                                                                          displacement_doc,
                                                                          material_densities)
      FreeCAD.closeDocument(doc.Name)
      FreeCAD.closeDocument(displacement_doc.Name)
      return physical_properties


   def save(self, file_save_path: str) -> None:
      """Saves the current assembly as a JSON graph file.

      Parameters
      ----------
      file_save_path : `str`
         Relative or absolute path of the desired output file.
      """

      # Create any necessary path directories
      file_path = Path(file_save_path).absolute().resolve()
      if not file_path.parent.exists():
         file_path.parent.mkdir()

      # Export the assembly to a JSON string and store as a file
      from .GraphAPI import export_to_json
      json_out = export_to_json(self)
      file_path.write_text(json_out)


   @staticmethod
   def load(file_name: str) -> Assembly:
      """Loads an assembly from the given JSON graph file.

      Parameters
      ----------
      file_name: `str`
         Relative or absolute path of the file containing a JSON-based Assembly.

      Returns
      -------
      `Assembly`
         The deserialized Assembly object represented by the specified file.
      """
      from .GraphAPI import import_from_json
      file_path = Path(file_name).absolute().resolve()
      if not file_path.exists():
         raise ValueError('The JSON graph file at "{}" does not exist'.format(str(file_path)))
      return import_from_json(file_path.read_text())


   # Cumulative properties of the entire assembly -------------------------------------------------

   @property
   def mass(self) -> float:
      """Mass (in `kg`) of the cumulative Assembly (read-only)."""
      return sum([part.mass for part in self.parts])

   @property
   def material_volume(self) -> float:
      """Material volume (in `m^3`) of the cumulative Assembly (read-only)."""
      return sum([part.material_volume for part in self.parts])

   @property
   def displaced_volume(self) -> float:
      """Displaced volume (in `m^3`) of the cumulative Assembly (read-only)."""
      return sum([part.displaced_volume for part in self.parts if part.is_exposed])

   @property
   def surface_area(self) -> float:
      """Surface/wetted area (in `m^2`) of the cumulative Assembly (read-only)."""
      return sum([part.surface_area for part in self.parts if part.is_exposed])

   @property
   def center_of_gravity(self) -> Coordinate:
      """Center of gravity (in `m`) of the Assembly (read-only)."""
      assembly = self.clone()
      assembly._place_parts()
      mass, center_of_gravity_x, center_of_gravity_y, center_of_gravity_z = (0.0, 0.0, 0.0, 0.0)
      for part in assembly.parts:
         part_mass = part.mass
         part_placement = part.static_placement
         part_center_of_gravity = part.oriented_center_of_gravity
         center_of_gravity_x += ((part_placement.x + part_center_of_gravity[0])
                                 * part_mass)
         center_of_gravity_y += ((part_placement.y + part_center_of_gravity[1])
                                 * part_mass)
         center_of_gravity_z += ((part_placement.z + part_center_of_gravity[2])
                                 * part_mass)
         mass += part_mass
      return Coordinate(assembly.name + '_center_of_gravity',
                        x=center_of_gravity_x / mass,
                        y=center_of_gravity_y / mass,
                        z=center_of_gravity_z / mass)

   @property
   def center_of_buoyancy(self) -> Coordinate:
      """Center of buoyancy (in `m`) of the Assembly (read-only)."""
      assembly = self.clone()
      assembly._place_parts()
      displaced_volume = 0.0
      center_of_buoyancy_x, center_of_buoyancy_y, center_of_buoyancy_z = (0.0, 0.0, 0.0)
      for part in assembly.parts:
         if part.is_exposed:
            part_placement = part.static_placement
            part_displaced_volume = part.displaced_volume
            part_center_of_buoyancy = part.oriented_center_of_buoyancy
            center_of_buoyancy_x += ((part_placement.x + part_center_of_buoyancy[0])
                                    * part_displaced_volume)
            center_of_buoyancy_y += ((part_placement.y + part_center_of_buoyancy[1])
                                    * part_displaced_volume)
            center_of_buoyancy_z += ((part_placement.z + part_center_of_buoyancy[2])
                                    * part_displaced_volume)
            displaced_volume += part_displaced_volume
      return Coordinate(assembly.name + '_center_of_buoyancy',
                        x=center_of_buoyancy_x / displaced_volume,
                        y=center_of_buoyancy_y / displaced_volume,
                        z=center_of_buoyancy_z / displaced_volume)

   @property
   def length(self) -> float:
      """X-axis length (in `m`) of the bounding box of the Assembly (read-only)."""
      assembly = self.clone()
      assembly._place_parts()
      minimum_extents_list = []
      maximum_extents_list = []
      for part in assembly.parts:
         pass  # TODO: Implement this
      return Max(*maximum_extents_list) - Min(*minimum_extents_list)

   @property
   def width(self) -> float:
      """Y-axis width (in `m`) of the bounding box of the Assembly (read-only)."""
      assembly = self.clone()
      assembly._place_parts()
      minimum_extents_list = []
      maximum_extents_list = []
      for part in assembly.parts:
         pass  # TODO: Implement this
      return Max(*maximum_extents_list) - Min(*minimum_extents_list)

   @property
   def height(self) -> float:
      """Z-axis height (in `m`) of the bounding box of the Assembly (read-only)."""
      assembly = self.clone()
      assembly._place_parts()
      minimum_extents_list = []
      maximum_extents_list = []
      for part in assembly.parts:
         pass
         #placement_center = \
         #   part._reorient_coordinate(part.static_origin.x * part.unoriented_length,
         #                             part.static_origin.y * part.unoriented_width,
         #                             part.static_origin.z * part.unoriented_height)
         #placement_z = part.static_placement.z - placement_center[2]
         #minimum_extents_list.append(placement_z)
         #maximum_extents_list.append(placement_z + part.oriented_height)
      return Max(*maximum_extents_list) - Min(*minimum_extents_list)
