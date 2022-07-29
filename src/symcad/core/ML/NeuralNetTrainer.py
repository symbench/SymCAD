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

from pathlib import Path
from typing import Dict, List, Tuple
from ..SymPart import SymPart
import io, tarfile, torch

class NeuralNetTrainer(object):
   """Private helper class to train a set of neural networks to learn the geometric properties
   of a given `SymPart`."""

   # Public attributes ----------------------------------------------------------------------------

   sympart: SymPart
   """`SymPart` whose geometric properties are being learned."""

   geometry: Dict[str, float]
   """Dictionary of geometric properties to learn."""

   networks: Dict[str, torch.nn.Module]
   """Dictionary of neural networks corresponding 1-to-1 to each geometric property to learn."""

   criteria: Dict[str, torch.nn.Module]
   """Dictionary of loss criteria corresponding to each neural network being trained."""

   optimizers: Dict[str, torch.optim.Optimizer]
   """Dictionary of training optimizers corresponding to each neural network being trained."""


   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, part: SymPart, cad_params_to_learn: List[str]) -> None:
      """Initializes a neural network trainer for the specified `part` and corresponding
      `cad_params_to_learn`.

      The available options for `cad_params_to_learn` are:

      - Lengths: `xlen`, `ylen`, `zlen`
      - Centers of Gravity: `cg_x`, `cg_y`, `cg_z`
      - Centers of Buoyancy: `cb_x`, `cb_y`, `cb_z`
      - Volume and Area: `material_volume`, `displaced_volume`, `surface_area`
      """
      super().__init__()
      self.sympart = part
      self.networks = {}
      self.criteria = {}
      self.optimizers = {}
      self.geometry = { key: 0 for key in part.geometry.__dict__.keys() - {'name'} }
      for cad_param in cad_params_to_learn:
         network = torch.nn.Sequential(
            torch.nn.Linear(len(self.geometry), 10),
            torch.nn.Tanh(),
            torch.nn.Linear(10, 1))
         self.networks[cad_param] = network
         self.criteria[cad_param] = torch.nn.MSELoss()
         self.optimizers[cad_param] = torch.optim.SGD(network.parameters(), lr=0.1)


   # Private helper methods -----------------------------------------------------------------------

   def _generate_data(self, num_points: int) -> Tuple[List[float], Dict[str, List[float]]]:

      # Generate all necessary PyTorch data structures
      inputs = torch.rand(num_points, len(self.geometry))
      outputs = { cad_param: torch.empty(num_points, 1) for cad_param in self.networks.keys() }

      # Determine the expected geometric outputs given the randomized input parameters
      datum = 0
      while datum < num_points:
         for idx, param in enumerate(self.geometry.keys()):
            self.geometry[param] = inputs[datum, idx].item()
         self.sympart.geometry.set(**self.geometry)
         try:
            props = self.sympart.get_cad_physical_properties()
         except Exception:
            inputs[datum] = torch.rand(len(self.geometry))
            continue
         for cad_param in self.networks.keys():
            outputs[cad_param][datum] = props[cad_param]
         datum += 1

      # Return all randomized inputs and their corresponding expected outputs
      return inputs, outputs


   # Public methods -------------------------------------------------------------------------------

   def learn_parameters(self, num_epochs: int, num_data_points_per_batch: int) -> None:
      """Trains the underlying neural network to learn all geometric properties as specified when
      the `NeuralNetTrainer` was created.

      Parameters
      ----------
      num_data_points_per_batch : `int`
         Number of geometric data points to include per training iteration.
      """

      # Ensure that all networks are in training mode
      for network in self.networks.values():
         network.train()

      # Train the neural network for the specified number of iterations
      for epoch in range(num_epochs):
         inputs, outputs = self._generate_data(num_data_points_per_batch)
         for network_name, network in self.networks.items():
            optimizer = self.optimizers[network_name]
            criterion = self.criteria[network_name]
            predicted_outputs = network(inputs)
            print(network_name, predicted_outputs, outputs[network_name])
            loss = criterion(predicted_outputs, outputs[network_name])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            print("Network: {}, Epoch: {} Loss: {}".format(network_name, epoch, loss.item()))


   def save(self, full_storage_path: str) -> None:
      """Stores the underlying trained neural networks as an XZ-compressed tarball at the
      location specified in `full_storage_path`."""

      # Create any necessary path directories
      file_path = Path(full_storage_path).absolute().resolve()
      if not file_path.parent.exists():
         file_path.parent.mkdir()

      # Convert all networks to TorchScript, save them, and zip them into a XZ tarball
      with tarfile.open(file_path, 'w:xz') as zip_file:
         param_order = ';'.join(self.geometry.keys())
         file_info = tarfile.TarInfo('param_order.txt')
         file_info.size = len(param_order)
         zip_file.addfile(file_info, io.BytesIO(param_order.encode('utf-8')))
         for network_name, network in self.networks.items():
            scripted_model = torch.jit.script(network.eval())
            model_bytes = torch.jit.freeze(scripted_model).save_to_buffer()
            file_info = tarfile.TarInfo(network_name + '.pt')
            file_info.size = len(model_bytes)
            zip_file.addfile(file_info, io.BytesIO(model_bytes))
