#!/usr/bin/env python3

from symcad.core.CAD import ModeledCad, ScriptedCad
from symcad.parts import Custom, Torisphere, Pipe
from PyFreeCAD.FreeCAD import FreeCAD, Part
from typing import Callable, Dict
from pathlib import Path
import os

def create_cad_pipe(params: Dict[str, float], fully_displace: bool) -> Part.Solid:
      height_mm = 1000.0 * params['height']
      outer_radius_mm = 1000.0 * params['radius']
      inner_radius_mm = 1000.0 * (params['radius'] - params['thickness'])
      if fully_displace:
         pipe = Part.makeCylinder(outer_radius_mm, height_mm)
      else:
         pipe2d = Part.makeRuledSurface(Part.makeCircle(outer_radius_mm),
                                        Part.makeCircle(inner_radius_mm))
         pipe = pipe2d.extrude(FreeCAD.Vector(0, 0, height_mm))
      return pipe


def run_cad_tests(delete_cad_models: bool):

   # Test built-in modeled construction (using Torisphere as a proxy)
   torisphere = Torisphere('TestTorisphere', 1000.0)
   assert torisphere.__cad__ is not None
   assert isinstance(torisphere.__cad__, ModeledCad)
   assert os.path.exists(torisphere.__cad__.cad_file_path)

   # Test built-in scripted construction (using Pipe as a proxy)
   pipe = Pipe('TestPipe', 1000.0)
   assert pipe.__cad__ is not None
   assert isinstance(pipe.__cad__, ScriptedCad)
   assert isinstance(pipe.__cad__.creation_callback, Callable)

   # Test custom modeled construction
   external_plate = Custom('TestCustomPlate',
                           os.path.realpath(os.path.dirname(__file__)) + '/test_plate.FCStd',
                           1000.0)
   assert external_plate.__cad__ is not None
   assert isinstance(external_plate.__cad__, ModeledCad)
   assert os.path.exists(external_plate.__cad__.cad_file_path)

   # Test custom modeled construction with CAD type conversion
   external_plate_converted = Custom('TestCustomPlateConverted',
                                     os.path.realpath(os.path.dirname(__file__)) + '/test_plate.stp',
                                     1000.0)
   assert external_plate_converted.__cad__ is not None
   assert isinstance(external_plate_converted.__cad__, ModeledCad)
   assert os.path.exists(external_plate_converted.__cad__.cad_file_path)

   # Test custom scripted construction
   external_pipe = Custom('TestCustomPipe', create_cad_pipe, 1000.0)
   assert external_pipe.__cad__ is not None
   assert isinstance(external_pipe.__cad__, ScriptedCad)
   assert isinstance(external_pipe.__cad__.creation_callback, Callable)

   # Test physical property retrieval from a built-in modeled construction
   concrete_params = {'base_radius': 0.22, 'radius': 0.22, 'crown_ratio': 1.0, 'knuckle_ratio': 0.06, 'height': 0.6, 'flange_radius': 0.08, 'thickness': 0.0025}
   props = torisphere.__cad__.get_physical_properties(concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1000.0, False)
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['mass'], float) and isinstance(props['surface_area'], float)

   # Test exporting the CAD model from a built-in modeled construction
   torisphere.__cad__.export_model('test_out_torisphere_builtin.FCStd', 'freecad', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   torisphere.__cad__.export_model('test_out_torisphere_builtin.stl', 'stl', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   torisphere.__cad__.export_model('test_out_torisphere_builtin.stp', 'step', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   if delete_cad_models:
      os.remove('test_out_torisphere_builtin.FCStd')
      os.remove('test_out_torisphere_builtin.stl')
      os.remove('test_out_torisphere_builtin.stp')

   # Test physical property retrieval from a built-in scripted construction
   props = pipe.__cad__.get_physical_properties(concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1000.0, True)
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['mass'], float) and isinstance(props['surface_area'], float)

   # Test exporting the CAD model from a built-in scripted construction
   pipe.__cad__.export_model('test_out_pipe_builtin.FCStd', 'freecad', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   pipe.__cad__.export_model('test_out_pipe_builtin.stl', 'stl', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   pipe.__cad__.export_model('test_out_pipe_builtin.stp', 'step', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   if delete_cad_models:
      os.remove('test_out_pipe_builtin.FCStd')
      os.remove('test_out_pipe_builtin.stl')
      os.remove('test_out_pipe_builtin.stp')

   # Test physical property retrieval from a custom modeled construction
   props = external_plate.__cad__.get_physical_properties(concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1000.0, False)
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['mass'], float) and isinstance(props['surface_area'], float)

   # Test exporting the CAD model from a custom modeled construction
   external_plate.__cad__.export_model('test_out_plate_external.FCStd', 'freecad', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_plate.__cad__.export_model('test_out_plate_external.stl', 'stl', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_plate.__cad__.export_model('test_out_plate_external.stp', 'step', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   if delete_cad_models:
      os.remove('test_out_plate_external.FCStd')
      os.remove('test_out_plate_external.stl')
      os.remove('test_out_plate_external.stp')

   # Test physical property retrieval from a custom modeled construction with CAD conversion
   props = external_plate_converted.__cad__.get_physical_properties(concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1000.0, True)
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['mass'], float) and isinstance(props['surface_area'], float)

   # Test exporting the CAD model from a custom modeled construction with CAD conversion
   external_plate_converted.__cad__.\
      export_model('test_out_plate_external_converted.FCStd', 'freecad', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_plate_converted.__cad__.\
      export_model('test_out_plate_external_converted.stl', 'stl', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_plate_converted.__cad__.\
      export_model('test_out_plate_external_converted.stp', 'step', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   if delete_cad_models:
      os.remove('test_out_plate_external_converted.FCStd')
      os.remove('test_out_plate_external_converted.stl')
      os.remove('test_out_plate_external_converted.stp')

   # Test physical property retrieval from a custom scripted construction
   props = external_pipe.__cad__.get_physical_properties(concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 1000.0, False)
   assert 'xlen' in props and 'ylen' in props and 'zlen' in props
   assert 'cg_x' in props and 'cg_y' in props and 'cg_z' in props
   assert 'cb_x' in props and 'cb_y' in props and 'cb_z' in props
   assert 'material_volume' in props and 'displaced_volume' in props
   assert 'surface_area' in props and 'mass' in props
   assert isinstance(props['xlen'], float) and isinstance(props['ylen'], float) and isinstance(props['zlen'], float)
   assert isinstance(props['cg_x'], float) and isinstance(props['cg_y'], float) and isinstance(props['cg_z'], float)
   assert isinstance(props['material_volume'], float) and isinstance(props['displaced_volume'], float)
   assert isinstance(props['mass'], float) and isinstance(props['surface_area'], float)

   # Test exporting the CAD model from a custom scripted construction
   external_pipe.__cad__.export_model('test_out_pipe_external.FCStd', 'freecad', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_pipe.__cad__.export_model('test_out_pipe_external.stl', 'stl', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   external_pipe.__cad__.export_model('test_out_pipe_external.stp', 'step', concrete_params, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
   if delete_cad_models:
      os.remove('test_out_pipe_external.FCStd')
      os.remove('test_out_pipe_external.stl')
      os.remove('test_out_pipe_external.stp')

   # Test adding CAD models to a FreeCAD document
   doc = FreeCAD.newDocument('Test')
   front_endcap_placement_point = (0.5, 0.5, 0.0)
   front_endcap_orientation = (0.0, -90.0, 0.0)
   front_endcap_placement = (0.0, 0.0, 0.0)
   center_pipe_placement_point = (0.5, 0.5, 1.0)
   center_pipe_orientation = (0.0, 90.0, 0.0)
   center_pipe_placement = (concrete_params['height'], 0.0, 0.0)
   rear_endcap_placement_point = (0.5, 0.5, 0.0)
   rear_endcap_orientation = (0.0, 90.0, 0.0)
   rear_endcap_placement = (concrete_params['height'], 0.0, 0.0)
   torisphere.__cad__.add_to_assembly('FrontEndcap', doc, concrete_params,
      front_endcap_placement_point, front_endcap_placement, front_endcap_orientation)
   torisphere.__cad__.add_to_assembly('RearEndcap', doc, concrete_params,
      rear_endcap_placement_point, rear_endcap_placement, rear_endcap_orientation)
   pipe.__cad__.add_to_assembly('CenterCylinder', doc, concrete_params,
      center_pipe_placement_point, center_pipe_placement, center_pipe_orientation)
   doc.saveAs('test_composite.FCStd')
   FreeCAD.closeDocument(doc.Name)
   if delete_cad_models:
      os.remove('test_composite.FCStd')

   # Clean up converted CAD models
   if delete_cad_models:
      os.remove(external_plate_converted.__cad__.cad_file_path)
      os.rmdir(Path(external_plate_converted.__cad__.cad_file_path).parent)
      for file in Path('.').glob('*.FCStd1'):
         file.unlink()


if __name__ == '__main__':

   run_cad_tests(True)
