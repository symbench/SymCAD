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

from .NeuralNetTrainer import NeuralNetTrainer
from typing import Dict, List, Optional
from ...core.SymPart import SymPart
from ..CAD import CadGeneral
from pathlib import Path
import io, tarfile, torch

class NeuralNet(object):
   """Private container that houses all neural networks for a given `SymPart`."""

   # Public attributes ----------------------------------------------------------------------------

   networks: Dict[str, torch.ScriptModule]
   """Dictionary of neural networks corresponding to each learned geometric property."""

   param_order: List[str]
   """List containing the expected input order of geometric parameters to each neural network."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, net_storage_path: str,
                      part: Optional[SymPart] = None,
                      auto_train_network: Optional[bool] = True) -> None:
      """Initializes a container to house all neural networks for the geometric properties of
      the given `part`.

      If `part` is not specified or is `None`, or if `auto_train_network` is set to `False`, a
      `RuntimeError` will be raised if the specified neural network does not already exist. If
      `auto_train_network` is `True` and no trained neural network exists, a new neural network
      will be trained to learn all available geometric properties for the specified `part`.
      """

      # Initialize NeuralNet data structure
      super().__init__()
      self.networks = {}
      self.param_order = []

      # Ensure that the neural network exists and has been trained
      net_file_path = CadGeneral.CAD_BASE_PATH.joinpath(net_storage_path).absolute().resolve()
      if not net_file_path.exists():
         net_file_path = Path(net_storage_path).absolute().resolve()
      if not net_file_path.exists():
         net_converted_path = Path('converted').joinpath(Path(net_storage_path).stem + '.tar.xz')
         net_file_path = CadGeneral.CAD_BASE_PATH.joinpath(net_converted_path)
      if not net_file_path.exists():
         if auto_train_network and part is not None:
            net_file_path = \
               CadGeneral.CAD_BASE_PATH.joinpath(net_storage_path).absolute().resolve()
            trainer = NeuralNetTrainer(part, ['xlen', 'ylen', 'zlen', 'cg_x', 'cg_y', 'cg_z',
                                              'cb_x', 'cb_y', 'cb_z', 'material_volume',
                                              'displaced_volume', 'surface_area'])
            trainer.learn_parameters(20, 32)
            trainer.save(str(net_file_path))
         else:
            raise RuntimeError('No trained neural network exists at "{}". '
                               'Set "auto_train_network" to True or manually train the '
                               'required network to continue'.format(net_storage_path))

      # Load and parse all trained neural networks within the specified tarball
      with tarfile.open(net_file_path, 'r:xz') as zip_file:
         for filename in zip_file.getnames():
            file = zip_file.extractfile(filename)
            if filename == 'param_order.txt':
               self.param_order = file.read().decode('utf-8').split(';')
            else:
               network_bytes = io.BytesIO(file.read())
               network_name = '.'.join(filename.split('.')[:-1])
               self.networks[network_name] = torch.jit.load(network_bytes)
               self.networks[network_name].eval()


   # Public methods -------------------------------------------------------------------------------

   def evaluate(self, property: str, **kwargs) -> float:
      """Evaluates the specified parameters in `**kwargs` through the neural network
      corresponding to the indicated geometric `property`.

      Parameters
      ----------
      property : `str`
         Geometric property for which the neural network should be evaluated. Available
         options (if a trained network exists for the corresponding property) are:
         - Lengths: `xlen`, `ylen`, `zlen`
         - Centers of Gravity: `cg_x`, `cg_y`, `cg_z`
         - Centers of Buoyancy: `cb_x`, `cb_y`, `cb_z`
         - Volume and Area: `material_volume`, `displaced_volume`, `surface_area`

      **kwargs : `Dict`
         Set of named parameters that define the underlying geometry of this part.

      Returns
      -------
      `float`
         The requested property as evaluated by the underlying neural network.
      """
      inputs = torch.empty(len(self.param_order))
      for idx, param in enumerate(self.param_order):
         inputs[idx] = kwargs.get(param)
      return self.networks[property](inputs).item()
