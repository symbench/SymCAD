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
from typing import Callable, Dict, Literal, Optional, Tuple
from PyFreeCAD.FreeCAD import FreeCAD, Part
from .CadGeneral import is_symbolic
from . import CadGeneral
from pathlib import Path

TESSELATION_VALUE = 1.0

class ScriptedCad(object):
   """Private helper class to generate a CAD representation from a `SymPart`."""

   # Public attributes ----------------------------------------------------------------------------

   creation_callback: Callable[[Dict[str, float], bool], Part.Solid]
   """Creation callback for a `SymPart` to generate a concrete OpenCascade model."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, creation_callback: Callable[[Dict[str, float], bool], Part.Solid]) -> None:
      """Initializes a `ScriptedCad` object, where `creation_callback` is a shape-specific
      method that uses a dictionary of `geometry: value` entries to create an OpenCascade
      `Part.Solid` for a given `SymPart`.
      """
      self.creation_callback = creation_callback


   # Built-in method implementations --------------------------------------------------------------

   def __eq__(self, other: ScriptedCad) -> bool:
      return self.creation_callback.__qualname__ == other.creation_callback.__qualname__


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

      # Verify that all parameters are concrete
      if is_symbolic(yaw_pitch_roll_deg[0]) or is_symbolic(yaw_pitch_roll_deg[1]) or \
                                               is_symbolic(yaw_pitch_roll_deg[2]):
         raise RuntimeError('The orientation of the part ("{}") must not be symbolic to add it '
                            'to a CAD assembly'.format(yaw_pitch_roll_deg))
      for key, val in concrete_parameters.items():
         if key != 'name' and is_symbolic(val):
            raise RuntimeError('The geometric parameter "{}" of the part must not be symbolic to '
                               'add it to a CAD assembly'.format(key))

      # Create and add a new CAD model to the assembly
      model = assembly.addObject(CadGeneral.PART_FEATURE_STRING, model_name)
      model.Shape = self.creation_callback(concrete_parameters, fully_displace)
      model.Shape.tessellate(TESSELATION_VALUE)
      assembly.recompute()

      # Properly place and orient the CAD model in the assembly
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector((1000.0 * placement_m[0]) - rotation_point.x,
                                 (1000.0 * placement_m[1]) - rotation_point.y,
                                 (1000.0 * placement_m[2]) - rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      model.Shape.tessellate(TESSELATION_VALUE)
      assembly.recompute()


   def get_physical_properties(self, concrete_parameters: Dict[str, float],
                                     placement_point: Tuple[float, float, float],
                                     yaw_pitch_roll_deg: Tuple[float, float, float],
                                     material_density_kg_m3: float) -> Dict[str, float]:
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

      Returns
      -------
      `Dict[str, float]`
         A dictionary containing all physical `SymPart` properties as computed using the
         underlying CAD model.
      """

      # Verify that all parameters are concrete
      if is_symbolic(yaw_pitch_roll_deg[0]) or is_symbolic(yaw_pitch_roll_deg[1]) or \
                                               is_symbolic(yaw_pitch_roll_deg[2]):
         raise RuntimeError('The orientation of the part ("{}") must not be symbolic to calculate '
                            'its physical properties from CAD'.format(yaw_pitch_roll_deg))
      for key, val in concrete_parameters.items():
         if key != 'name' and is_symbolic(val):
            raise RuntimeError('The geometric parameter "{}" of the part must not be symbolic to '
                               'calculate its physical properties from CAD'.format(key))
      placement_point = [0.0 if is_symbolic(p) else float(p) for p in placement_point]

      # Create the scripted CAD model
      doc = FreeCAD.newDocument()
      model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'Model')
      model.Shape = self.creation_callback(concrete_parameters, False)
      model.Shape.tessellate(TESSELATION_VALUE)
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector(-rotation_point.x, -rotation_point.y, -rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      model.Shape.tessellate(TESSELATION_VALUE)

      # Create a separate displacement model
      displaced_model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'DisplacedModel')
      displaced_model.Shape = self.creation_callback(concrete_parameters, True)
      displaced_model.Shape.tessellate(TESSELATION_VALUE)
      displaced_model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      displaced_model.Shape.tessellate(TESSELATION_VALUE)

      # Retrieve all physical model properties
      doc.recompute()
      properties = CadGeneral.fetch_model_physical_properties(model.Shape,
                                                              displaced_model.Shape,
                                                              material_density_kg_m3)
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

      # Create and tessellate the scripted CAD model
      doc = FreeCAD.newDocument()
      model = doc.addObject(CadGeneral.PART_FEATURE_STRING, 'Model')
      model.Shape = self.creation_callback(concrete_parameters, False)
      model.Shape.tessellate(TESSELATION_VALUE)
      rotation_point = CadGeneral.compute_placement_point(model.Shape, placement_point)
      placement = FreeCAD.Vector(-rotation_point.x, -rotation_point.y, -rotation_point.z)
      rotation = FreeCAD.Rotation(*yaw_pitch_roll_deg)
      model.Placement = FreeCAD.Placement(placement, rotation, rotation_point)
      model.Shape.tessellate(TESSELATION_VALUE)
      doc.recompute()

      # Create the requested CAD format of the model
      CadGeneral.save_model(file_path, model_type, model)
      FreeCAD.closeDocument(doc.Name)
