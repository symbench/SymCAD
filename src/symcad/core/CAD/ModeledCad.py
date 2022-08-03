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
from typing import Dict, Literal, Optional, Tuple
from PyFreeCAD.FreeCAD import FreeCAD, Mesh, Part
from .CadGeneral import is_symbolic
from . import CadGeneral
from pathlib import Path

TESSELATION_VALUE = 1.0

class ModeledCad(object):
   """Private helper class to connect a `SymPart` to an existing CAD representation."""

   # Public attributes ----------------------------------------------------------------------------

   cad_file_path: str
   """Absolute path of the representative CAD model for a given `SymPart`."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, cad_file_name: str) -> None:
      """Initializes a `ModeledCad` object, where `cad_file_name` indicates a representative
      CAD model for a `SymPart` relative to the `src/cad` directory.
      """
      self._store_absolute_cad_file_path(cad_file_name)


   # Built-in method implementations --------------------------------------------------------------

   def __eq__(self, other: ModeledCad) -> bool:
      return self.cad_file_path == other.cad_file_path


   # Private helper methods -----------------------------------------------------------------------

   def _store_absolute_cad_file_path(self, cad_file_name: str) -> None:
      """Determines and stores the full absolute path to the specified `cad_file_name`, converting
      a non-native model into the FreeCAD format if necessary.

      Parameters
      ----------
      cad_file_name : `str`
         Name of the representative CAD file model relative to this project's `src/cad` directory.
      """

      # Create an internal FreeCAD file if importing from another format
      file_extension = Path(cad_file_name).suffix.casefold()
      if file_extension != '.fcstd':

         # Update the target CAD file paths
         file_path = Path(cad_file_name).absolute().resolve()
         cad_file_name = Path('converted').joinpath(Path(cad_file_name).stem + '.FCStd')
         cad_file_path = CadGeneral.CAD_BASE_PATH.joinpath(cad_file_name)
         if not cad_file_path.exists():

            # Determine the type of file to import
            if (file_extension == '.stp') or (file_extension == '.step'):
               doc = FreeCAD.newDocument(cad_file_path.stem)
               model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'Model')
               shape = Part.Shape()
               shape.read(str(file_path))
               model.Shape = shape
               doc.saveAs(str(cad_file_path))
               FreeCAD.closeDocument(doc.Name)

            elif file_extension == '.stl':
               doc = FreeCAD.newDocument(cad_file_path.stem)
               model = doc.addObject('Mesh::Feature', 'Model')
               model.Mesh = Mesh.Mesh(str(file_path))
               doc.saveAs(str(cad_file_path))
               FreeCAD.closeDocument(doc.Name)

            else:
               raise NotImplementedError('CAD files of type {} are not yet supported!'
                                          .format(file_extension))

      # Store the absolute CAD file path
      self.cad_file_path = \
            str(CadGeneral.CAD_BASE_PATH.joinpath(cad_file_name).absolute().resolve())


   # Public methods -------------------------------------------------------------------------------

   def add_to_assembly(self, model_name: str,
                             assembly: FreeCAD.Document,
                             concrete_parameters: Dict[str, float],
                             placement_point: Tuple[float, float, float],
                             placement_m: Tuple[float, float, float],
                             yaw_pitch_roll_deg: Tuple[float, float, float],
                             fully_displace: Optional[bool] = False) -> None:
      """Adds a CAD model representation of the `SymPart` to the specified assembly.

      Parameters
      ----------
      model_name : `str`
         Desired name for the CAD model.
      assembly : `FreeCAD.Document`
         FreeCAD assembly document to which the CAD model should be added.
      concrete_parameters : `Dict[str, float]`
         Dictionary of free variables along with their desired concrete values.
      placement_point : `Tuple[float, float, float]`
         Local coordinate (in percent length) to be used for the center of rotation and placement
         of the CAD model.
      placement_m : `Tuple[float, float, float]`
         Global xyz-placement (in `m`) of the `placement_point` of the CAD object in the assembly.
      yaw_pitch_roll_deg : `Tuple[float, float, float]`
         Global yaw-, pitch-, and roll-orientation in degrees of the CAD object.
      fully_displace : `bool`
         Whether to create a fully solid CAD model for displacement purposes.
      """

      # Verify that all parameters have concrete representations
      if is_symbolic(yaw_pitch_roll_deg[0]) or is_symbolic(yaw_pitch_roll_deg[1]) or \
                                               is_symbolic(yaw_pitch_roll_deg[2]):
         raise RuntimeError('The orientation of the part ("{}") must not be symbolic to add it '
                            'to a CAD assembly'.format(yaw_pitch_roll_deg))
      for key, val in concrete_parameters.items():
         if key != 'name' and is_symbolic(val):
            raise RuntimeError('The geometric parameter "{}" of the part must not be symbolic to '
                               'add it to a CAD assembly'.format(key))

      # Concretize the CAD model if it is parametric
      doc = FreeCAD.open(self.cad_file_path)
      CadGeneral.assign_free_parameter_values(self.cad_file_path, doc, concrete_parameters)

      # Determine if the SymPart contains a separate displacement model
      if fully_displace and len(doc.getObjectsByLabel('DisplacedModel')) > 0:
         model = doc.getObjectsByLabel('DisplacedModel')[0]
      else:
         model = doc.getObjectsByLabel('Model')[0]

      # Parse the CAD model as a solid if it is currently a mesh
      if hasattr(model, 'Mesh'):
         shape = Part.Shape()
         shape.makeShapeFromMesh(model.Mesh.Topology, 0.1)
         model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'Model')
         model.Shape = Part.Solid(shape)

      # Create and add a new CAD model to the assembly
      cad_object = assembly.addObject(CadGeneral.PART_FEATURE_STRING, model_name)
      cad_object.Shape = Part.getShape(model, '', needSubElement=False, refine=False)
      cad_object.Shape.tessellate(TESSELATION_VALUE)
      assembly.recompute()

      # Properly place and orient the CAD model in the assembly
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector((1000.0 * placement_m[0]) - rotation_point.x,
                                 (1000.0 * placement_m[1]) - rotation_point.y,
                                 (1000.0 * placement_m[2]) - rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      cad_object.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      cad_object.Shape.tessellate(TESSELATION_VALUE)
      assembly.recompute()
      FreeCAD.closeDocument(doc.Name)


   def get_physical_properties(self, concrete_parameters: Dict[str, float],
                                     placement_point: Tuple[float, float, float],
                                     yaw_pitch_roll_deg: Tuple[float, float, float],
                                     material_density_kg_m3: float,
                                     normalize_origin: bool) -> Dict[str, float]:
      """Returns all physical properties of the CAD model.

      Mass properties will be computed assuming a uniform material density as specified in
      the `material_density_kg_m3` parameter.

      All free parameters within the CAD model must be concretized by passing in an appropriate
      `concrete_parameters` dictionary containing the names of the free parameters as its keys,
      along with their corresponding concrete floating-point values.

      Parameters
      ----------
      concrete_parameters : `Dict[str, float]`
         Dictionary of free variables along with their desired concrete values.
      placement_point : `Tuple[float, float, float]`
         Local coordinate (in percent length) to be used for the center of placement
         of the CAD model.
      yaw_pitch_roll_deg : `Tuple[float, float, float]`
         Global yaw-, pitch-, and roll-orientation in degrees of the CAD object.
      material_density_kg_m3 : `float`
         Uniform material density to be used in mass property calculations (in `kg/m^3`).
      normalize_origin : `bool`
         Return physical properties with respect to the front, left, bottom corner of the
         underlying CAD model.

      Returns
      -------
      `Dict[str, float]`
         A dictionary containing all physical `SymPart` properties as computed using the
         underlying CAD model.
      """

      # Verify that all parameters have concrete representations
      if is_symbolic(yaw_pitch_roll_deg[0]) or is_symbolic(yaw_pitch_roll_deg[1]) or \
                                               is_symbolic(yaw_pitch_roll_deg[2]):
         raise RuntimeError('The orientation of the part ("{}") must not be symbolic to calculate '
                            'its physical properties from CAD'.format(yaw_pitch_roll_deg))
      for key, val in concrete_parameters.items():
         if key != 'name' and is_symbolic(val):
            raise RuntimeError('The geometric parameter "{}" of the part must not be symbolic to '
                               'calculate its physical properties from CAD'.format(key))
      placement_point = [0.0 if is_symbolic(p) else float(p) for p in placement_point]

      # Concretize the CAD model if it is parametric
      doc = FreeCAD.open(self.cad_file_path)
      CadGeneral.assign_free_parameter_values(self.cad_file_path, doc, concrete_parameters)

      # Recompute and parse the CAD model as a solid
      if hasattr(doc.getObjectsByLabel('Model')[0], 'Mesh'):
         shape = Part.Shape()
         shape.makeShapeFromMesh(doc.getObjectsByLabel('Model')[0].Mesh.Topology, 0.1)
         model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'Model')
         model.Shape = Part.Solid(shape)
      else:
         model = doc.getObjectsByLabel('Model')[0]

      # Orient and tessellate the model
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector(-rotation_point.x, -rotation_point.y, -rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      model.Shape.tessellate(TESSELATION_VALUE)
      doc.recompute()

      # Determine if the SymPart contains a separate displacement model
      if len(doc.getObjectsByLabel('DisplacedModel')) > 0:
         displaced_model = doc.getObjectsByLabel('DisplacedModel')[0]
         displaced_model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
         displaced_model.Shape.tessellate(TESSELATION_VALUE)
         doc.recompute()
         displaced_model = displaced_model.Shape
      else:
         displaced_model = model.Shape
      model = model.Shape

      # Retrieve all physical model properties
      properties = CadGeneral.fetch_model_physical_properties(model,
                                                              displaced_model,
                                                              material_density_kg_m3,
                                                              normalize_origin)
      FreeCAD.closeDocument(doc.Name)
      return properties


   def export_model(self, file_save_path: str,
                          model_type: Literal['freecad', 'step', 'stl'],
                          concrete_parameters: Dict[str, float],
                          placement_point: Tuple[float, float, float],
                          yaw_pitch_roll_deg: Tuple[float, float, float]) -> None:
      """Creates a CAD model of the `SymPart` in the specified format.

      Parameters
      ----------
      file_save_path : `str`
         Output file path at which to store the generated CAD model.
      model_type : {'freecad', 'step', 'stl'}
         Format of the CAD model to export.
      concrete_parameters : `Dict[str, float]`
         Dictionary of free variables along with their desired concrete values.
      placement_point : `Tuple[float, float, float]`
         Local coordinate (in percent length) to be used for the center of placement
         of the CAD model.
      yaw_pitch_roll_deg : `Tuple[float, float, float]`
         Global yaw-, pitch-, and roll-orientation in degrees of the CAD object.
      """

      # Verify that all parameters have concrete representations
      if is_symbolic(yaw_pitch_roll_deg[0]) or is_symbolic(yaw_pitch_roll_deg[1]) or \
                                               is_symbolic(yaw_pitch_roll_deg[2]):
         raise RuntimeError('The orientation of the part ("{}") must not be symbolic to export '
                            'it as a CAD model'.format(yaw_pitch_roll_deg))
      for key, val in concrete_parameters.items():
         if key != 'name' and is_symbolic(val):
            raise RuntimeError('The geometric parameter "{}" of the part must not be symbolic to '
                               'export it as a CAD model'.format(key))
      placement_point = [0.0 if is_symbolic(p) else float(p) for p in placement_point]

      # Create any necessary path directories
      file_path = Path(file_save_path).absolute().resolve()
      if not file_path.parent.exists():
         file_path.parent.mkdir()

      # Concretize the CAD model if it is parametric
      doc = FreeCAD.open(self.cad_file_path)
      CadGeneral.assign_free_parameter_values(self.cad_file_path, doc, concrete_parameters)

      # Orient and tessellate the model
      model = doc.getObjectsByLabel('Model')[0]
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector(-rotation_point.x, -rotation_point.y, -rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      model.Shape.tessellate(TESSELATION_VALUE)
      doc.recompute()

      # Create the requested CAD format of the model
      CadGeneral.save_model(file_path, model_type, model)
      FreeCAD.closeDocument(doc.Name)
