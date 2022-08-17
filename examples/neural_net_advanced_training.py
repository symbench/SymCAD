#!/usr/bin/env python3

# This should never be publically accessed, for internal use only
from symcad.core.ML import NeuralNetTrainer
from symcad.parts import Cuboid
from pathlib import Path

# Create a simple Cuboid for training
part = Cuboid('TrainerBox')

# Create a trainer and learn some physical properties of interest
trainer = NeuralNetTrainer(part, ['material_volume', 'cg_z'])
trainer.learn_parameters(32)
trainer.save(Path(__file__).parent.joinpath('MyCustomBox.tar.xz'))
