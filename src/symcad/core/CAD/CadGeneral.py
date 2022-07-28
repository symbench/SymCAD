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

"""Private helper module for manipulating FreeCAD models."""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Literal, Tuple, Union
from PyFreeCAD.FreeCAD import FreeCAD, Part
import zipfile

PART_FEATURE_STRING = 'Part::Feature'

def is_symbolic(val: Any) -> bool:
   """Returns whether `val` is a symbolic parameter."""
   try:
      float(val)
      return False
   except Exception:
      return True


def get_free_parameters_from_model(cad_file_path: str,
                                   document: Union[FreeCAD.Document, None]) -> List[str]:
   """Returns all free parameters specified within the CAD model.

   Free parameters are defined as aliased cells in a FreeCAD spreadsheet with the title
   `Parameters` which occur before an optional row in the same spreadsheet with a cell
   containing the word `Derived`.

   Parameters
   ----------
   cad_file_path : `str`
      Absolute path of the CAD model.
   document : `Union[FreeCAD.Document, None]`
      An existing open FreeCAD document or `None` if no open document already exists.

   Returns
   -------
   `List[str]`
      The list of free parameters in the CAD model.
   """

   # Determine if the file corresponds to a parametric CAD model
   parameters = []
   doc = FreeCAD.open(cad_file_path) if document is None else document
   if len(doc.getObjectsByLabel('Parameters')) > 0:

      # Parse all free parameters inside the model
      params = doc.getObjectsByLabel('Parameters')[0]
      aliases = params.cells.Content.split('Derived')[0].split('alias="')
      for idx in range(1, len(aliases)):
         parameters.append(aliases[idx].split('"')[0])

   # Return the list of free parameters
   if document is None:
      FreeCAD.closeDocument(doc.Name)
   return parameters


def get_free_parameters_from_method(creation_method: Callable[[Dict[str, float], bool],
                                                              Part.Solid]) -> List[str]:
   """Returns all free parameters required by the specified CAD creation method.

   Free parameters are defined as variables that are expected to be concretely defined within
   the `parameters` dictionary passed to the `creation_method` in order to generate a CAD model.

   Parameters
   ----------
   creation_method : `Callable[[Dict[str, float], bool], Part.Solid]`
      Callable method that can be used to create a CAD model.

   Returns
   -------
   `List[str]`
      The list of free parameters required by the CAD generation method.
   """
   params = {}
   new_parameter_parsed = True
   for displaced in [False, True]:
      while new_parameter_parsed:
         try:
            new_parameter_parsed = False
            creation_method(params, displaced)
         except KeyError as key:
            new_parameter_parsed = True
            params[str(key).strip("\"'")] = 1.0
   return list(params)


def assign_free_parameter_values(cad_file_path: str,
                                 doc: FreeCAD.Document,
                                 concrete_parameters: Dict[str, float]) -> None:
   """Assigns concrete values to all free parameters specified within the CAD model.

   Free parameters are defined as aliased cells in a FreeCAD spreadsheet with the title
   `Parameters` which occur before an optional row in the same spreadsheet with a cell
   containing the word `Derived`.

   Parameters
   ----------
   cad_file_path : `str`
      Absolute path of the CAD model.
   document : `FreeCAD.Document`
      An existing open FreeCAD document.
   concrete_parameters : `Dict[str, float]`
      Dictionary of free variables along with their desired concrete values.
   """
   if len(doc.getObjectsByLabel('Parameters')) > 0:

      # Ensure that all free parameters have concrete representations
      missing_params = [key for key in get_free_parameters_from_model(cad_file_path, doc)
                                    if key not in concrete_parameters]
      if missing_params:
         raise RuntimeError('CAD model contains symbolic free parameters without concrete '
                            'floating-point representations: {}'.format(missing_params))

      # Assign concrete values to all symbolic free parameters
      params = doc.getObjectsByLabel('Parameters')[0]
      for param in get_free_parameters_from_model(cad_file_path, doc):
         units = 'm' if ' m' in str(params.get(params.getCellFromAlias(param))) else ''
         params.set(params.getCellFromAlias(param), str(concrete_parameters[param]) + units)
      doc.recompute()


def compute_placement_point(part: Part.Solid,
                            origin: Tuple[float, float, float]) -> FreeCAD.Vector:
   """Computes the global placement point (in `mm`) of the CAD model based on the specified
   percent-length `origin` values.

   Parameters
   ----------
   part : `Part.Solid`
      The CAD part for which the placement point is being computed.
   origin : `Tuple[float, float, float]`
      Local coordinate (in percent length) to be used for the center of placement and rotation
      of the CAD part.

   Returns
   -------
   `Tuple[float, float, float]`
      The absolute placement point of the CAD model (in `mm`) in its FreeCAD representation format.
   """
   placement_point_x = origin[0] * \
      float(FreeCAD.Units.Quantity(part.BoundBox.XLength, FreeCAD.Units.Length).getValueAs('mm'))
   placement_point_y = origin[1] * \
      float(FreeCAD.Units.Quantity(part.BoundBox.YLength, FreeCAD.Units.Length).getValueAs('mm'))
   placement_point_z = origin[2] * \
      float(FreeCAD.Units.Quantity(part.BoundBox.ZLength, FreeCAD.Units.Length).getValueAs('mm'))
   return FreeCAD.Vector(
      float(FreeCAD.Units.Quantity(part.BoundBox.XMin, FreeCAD.Units.Length).getValueAs('mm'))\
            + placement_point_x,
      float(FreeCAD.Units.Quantity(part.BoundBox.YMin, FreeCAD.Units.Length).getValueAs('mm'))\
            + placement_point_y,
      float(FreeCAD.Units.Quantity(part.BoundBox.ZMin, FreeCAD.Units.Length).getValueAs('mm'))\
            + placement_point_z)


def fetch_model_physical_properties(model: Part.Feature,
                                    displaced_model: Union[Part.Feature, None],
                                    material_density_kg_m3: float) -> Dict[str, float]:
   """Returns all physical properties of the specified CAD model.

   Mass properties will be computed assuming a uniform material density as specified in
   the `material_density_kg_m3` parameter.

   Parameters
   ----------
   model : `Part.Feature`
      CAD model for which to compute the geometric properties.
   displaced_model : `Union[Part.Feature, None]`
      CAD model for which to compute the geometric properties assuming full displacement
      of a solid.
   material_density_kg_m3 : `float`
      Uniform material density to be used in mass property calculations (in `kg/m^3`).

   Returns
   -------
   `Dict[str, float]`
      A dictionary containing all physical properties of the underlying CAD model.
   """
   return {
      'xlen': float(FreeCAD.Units.Quantity(model.BoundBox.XLength, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'ylen': float(FreeCAD.Units.Quantity(model.BoundBox.YLength, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'zlen': float(FreeCAD.Units.Quantity(model.BoundBox.ZLength, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'min_x': float(FreeCAD.Units.Quantity(model.BoundBox.XMin, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'min_y': float(FreeCAD.Units.Quantity(model.BoundBox.YMin, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'min_z': float(FreeCAD.Units.Quantity(model.BoundBox.ZMin, FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'cg_x': float(FreeCAD.Units.Quantity(model.CenterOfGravity[0], FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'cg_y': float(FreeCAD.Units.Quantity(model.CenterOfGravity[1], FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'cg_z': float(FreeCAD.Units.Quantity(model.CenterOfGravity[2], FreeCAD.Units.Length)
                                 .getValueAs('m')),
      'cb_x': float(FreeCAD.Units.Quantity(displaced_model.CenterOfGravity[0],
                                           FreeCAD.Units.Length).getValueAs('m'))
                                           if displaced_model is not None else 0.0,
      'cb_y': float(FreeCAD.Units.Quantity(displaced_model.CenterOfGravity[1],
                                           FreeCAD.Units.Length).getValueAs('m'))
                                           if displaced_model is not None else 0.0,
      'cb_z': float(FreeCAD.Units.Quantity(displaced_model.CenterOfGravity[2],
                                           FreeCAD.Units.Length).getValueAs('m'))
                                           if displaced_model is not None else 0.0,
      'mass': float(FreeCAD.Units.Quantity(model.Volume, FreeCAD.Units.Volume)
                                 .getValueAs('m^3') * material_density_kg_m3),
      'material_volume': float(FreeCAD.Units.Quantity(model.Volume, FreeCAD.Units.Volume)
                                 .getValueAs('m^3')),
      'displaced_volume': float(FreeCAD.Units.Quantity(displaced_model.Volume,
                                                         FreeCAD.Units.Volume)
                                 .getValueAs('m^3')) if displaced_model is not None else 0.0,
      'surface_area': float(FreeCAD.Units.Quantity(displaced_model.Area, FreeCAD.Units.Area)
                                 .getValueAs('m^2')) if displaced_model is not None else 0.0
   }


def fetch_assembly_physical_properties(assembly: FreeCAD.Document,
                                       displaced: FreeCAD.Document,
                                       material_densities: Dict[str, float]) -> Dict[str, float]:
   """Returns all physical properties of the specified CAD assembly.

   Mass properties will be computed assuming each constituent part has a uniform material density
   as specified by its corresponding value in `kg/m^3` in the `material_densities` parameter.

   Parameters
   ----------
   assembly : `FreeCAD.Document`
      CAD assembly for which to compute the geometric properties.
   displaced : `FreeCAD.Document`
      CAD assembly for which to compute the geometric properties assuming full displacement
      of a solid.
   material_densities : `Dict[str, float]`
      Uniform material densities to be used in mass property calculations (in `kg/m^3`).

   Returns
   -------
   `Dict[str, float]`
      A dictionary containing all physical properties of the underlying CAD assembly.
   """
   xlen_min = ylen_min = zlen_min = 100000000.0
   xlen_max = ylen_max = zlen_max = -100000000.0
   props = { 'xlen': 0.0, 'ylen': 0.0, 'zlen': 0.0,
             'cg_x': 0.0, 'cg_y': 0.0, 'cg_z': 0.0, 'cb_x': 0.0, 'cb_y': 0.0, 'cb_z': 0.0,
             'mass': 0.0, 'material_volume': 0.0, 'displaced_volume': 0.0, 'surface_area': 0.0 }
   for part in assembly.Objects:
      displaced_part = [obj for obj in displaced.Objects if obj.Label == part.Label]
      displaced_part = None if not displaced_part else displaced_part[0]
      part_props = fetch_model_physical_properties(part.Shape,
                                                   displaced_part.Shape,
                                                   material_densities[part.Label])
      props['cg_x'] += (part_props['cg_x'] * part_props['mass'])
      props['cg_y'] += (part_props['cg_y'] * part_props['mass'])
      props['cg_z'] += (part_props['cg_z'] * part_props['mass'])
      props['cb_x'] += (part_props['cb_x'] * part_props['displaced_volume'])
      props['cb_y'] += (part_props['cb_y'] * part_props['displaced_volume'])
      props['cb_z'] += (part_props['cb_z'] * part_props['displaced_volume'])
      props['mass'] += part_props['mass']
      props['material_volume'] += part_props['material_volume']
      props['displaced_volume'] += part_props['displaced_volume']
      props['surface_area'] += part_props['surface_area']
      xlen_min = min(xlen_min,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.XMin, FreeCAD.Units.Length)
                                  .getValueAs('m'))
      ylen_min = min(ylen_min,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.YMin, FreeCAD.Units.Length)
                                  .getValueAs('m'))
      zlen_min = min(zlen_min,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.ZMin, FreeCAD.Units.Length)
                                  .getValueAs('m'))
      xlen_max = max(xlen_max,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.XMax, FreeCAD.Units.Length)
                                  .getValueAs('m'))
      ylen_max = max(ylen_max,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.YMax, FreeCAD.Units.Length)
                                  .getValueAs('m'))
      zlen_max = max(zlen_max,
                     FreeCAD.Units.Quantity(part.Shape.BoundBox.ZMax, FreeCAD.Units.Length)
                                  .getValueAs('m'))
   props['xlen'] = xlen_max - xlen_min
   props['ylen'] = ylen_max - ylen_min
   props['zlen'] = zlen_max - zlen_min
   props['cg_x'] /= props['mass']
   props['cg_y'] /= props['mass']
   props['cg_z'] /= props['mass']
   props['cb_x'] /= props['displaced_volume']
   props['cb_y'] /= props['displaced_volume']
   props['cb_z'] /= props['displaced_volume']
   return props


def retrieve_interferences(assembly: FreeCAD.Document) -> List[Tuple[str, str]]:
   """Retrieves a list of components within the CAD model that interfere or overlap
   with any other contained components.

   Parameters
   ----------
   assembly : `FreeCAD.Document`
      CAD assembly in which to search for interfering components.

   Returns
   -------
   `List[Tuple[str, str]]`
      A list of tuples containing CAD components that interfere with one another.
   """
   interferences = []
   for idx1, component1 in enumerate(assembly.Objects):
      for idx2, component2 in enumerate(assembly.Objects):
         if idx2 > idx1:
            overlap = FreeCAD.Units.Quantity(component1.Shape.common(component2.Shape).Volume,
                                             FreeCAD.Units.Volume).getValueAs('m^3')
            if overlap > 0.02:
               interferences.append((component1.Label, component2.Label))
   return interferences


def save_model(file_path: str,
               model_type: Literal['freecad', 'step', 'stl'],
               model: Part.Feature) -> None:
   """Saves a CAD model in the specified format.

   Parameters
   ----------
   file_path : `str`
      Output file path at which to store the CAD model.
   model_type : {'freecad', 'step', 'stl'}
      Format of the CAD model to store.
   model : `Part.Feature`
      The actual CAD model being stored.
   """
   if model_type == 'freecad':
      file_path = str(file_path) if file_path.suffix.casefold() == '.fcstd' else \
                  str(file_path) + '.FCStd'
      model.Document.saveAs(file_path)
      write_freecad_gui_doc(file_path, model, False)
   elif model_type == 'step':
      file_path = str(file_path) if file_path.suffix.casefold() == '.step' or \
                                    file_path.suffix.casefold() == '.stp' else \
                  str(file_path) + '.stp'
      model.Shape.exportStep(file_path)
   elif model_type == 'stl':
      from PyFreeCAD.FreeCAD import Mesh
      file_path = str(file_path) if file_path.suffix.casefold() == '.stl' else \
                  str(file_path) + '.stl'
      Mesh.export([model], file_path)
   else:
      raise TypeError('Exporting to the "{}" CAD format is not currently supported'
                      .format(model_type))


def save_assembly(file_path: str,
                  cad_type: Literal['freecad', 'step', 'stl'],
                  assembly: FreeCAD.Document) -> None:
   """Saves a CAD assembly in the specified format.

   Parameters
   ----------
   file_path : `str`
      Output file path at which to store the CAD assembly.
   cad_type : {'freecad', 'step', 'stl'}
      Format of the CAD model to store.
   assembly : `FreeCAD.Document`
      The actual CAD assembly being stored.
   """
   if cad_type == 'freecad':
      file_path = str(file_path) if file_path.suffix.casefold() == '.fcstd' else \
                  str(file_path) + '.FCStd'
      assembly.saveAs(file_path)
      write_freecad_gui_doc(file_path, assembly, True)
   elif cad_type == 'step':
      from PyFreeCAD.FreeCAD import Import
      file_path = str(file_path) if file_path.suffix.casefold() == '.step' or \
                                    file_path.suffix.casefold() == '.stp' else \
                  str(file_path) + '.stp'
      Import.export(assembly.Objects, file_path)
   elif cad_type == 'stl':
      from PyFreeCAD.FreeCAD import Mesh
      file_path = str(file_path) if file_path.suffix.casefold() == '.stl' else \
                  str(file_path) + '.stl'
      Mesh.export(assembly.Objects, file_path)
   else:
      raise TypeError('Exporting to the "{}" CAD format is not currently supported'
                      .format(cad_type))


def write_freecad_gui_doc(file_path: str,
                          model: Union[FreeCAD.Document, Part.Feature],
                          is_assembly: bool) -> None:
   """Adds a GuiDocument.xml file to the specified FreeCAD model document.

   This document allows the FreeCAD software to know how to set the initial orientation,
   visibility, and placement of the model in its viewport.

   Parameters
   ----------
   file_path : `str`
      Path to an existing FreeCAD model file.
   model : `Union[FreeCAD.Document, Part.Feature]`
      The current model or assembly that resides within the FreeCAD file.
   is_assembly : `bool`
      Whether the model is a full assembly or a standalone part.
   """

   # Parse the relevant model details
   num_models = 1 if not is_assembly else len(model.Objects)

   # Create the GuiDocument.xml file contents
   contents  = '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<Document SchemaVersion="1" HasExpansion="1">\n'
   contents += '    <Expand />\n    <ViewProviderData Count="' + str(num_models) + '">\n'
   for i in range(num_models):
      current_model = model if not is_assembly else model.Objects[i]
      contents += '        <ViewProvider name="' + current_model.Label + '" expanded="0">\n            <Properties Count="4" TransientCount="0">\n'
      contents += '                <Property name="DisplayMode" type="App::PropertyEnumeration" status="1">\n                    <Integer value="0"/>\n                </Property>\n'
      contents += '                <Property name="ShowInTree" type="App::PropertyBool" status="1">\n                    <Bool value="true"/>\n                </Property>\n'
      contents += '                <Property name="Transparency" type="App::PropertyPercent" status="1">\n                    <Integer value="0"/>\n                </Property>\n'
      contents += '                <Property name="Visibility" type="App::PropertyBool" status="1">\n                    <Bool value="true"/>\n                </Property>\n'
      contents += '            </Properties>\n        </ViewProvider>\n'
   contents += '    </ViewProviderData>\n'
   contents += '    <Camera settings="OrthographicCamera {&#10;  viewportMapping ADJUST_CAMERA&#10;  orientation 1 0 0  1.5707965&#10;  aspectRatio 1&#10;}&#10;"/>\n</Document>\n'

   # Add the GuiDocument.xml contents to the FreeCAD file
   with zipfile.ZipFile(file_path, 'a', zipfile.ZIP_DEFLATED) as file:
      file.writestr('GuiDocument.xml', contents)
