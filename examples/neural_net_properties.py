#!/usr/bin/env python3

# This should never be publically accessed, for internal use only
from symcad.core.ML import NeuralNet
from pathlib import Path

# Manually instantiate the pretrained neural network for a custom box
network_path = Path(__file__).parent.joinpath('MyCustomBox.tar.xz')
net = NeuralNet('MyCustomBox', network_path)
print('MyCustomBox geometric parameters: {}\n'.format(net.param_order))

# Output some learned material volume properties for random geometries
print('Material Volume @ length = 0.1 m, width = 0.1 m, height = 0.1 m: ', net.evaluate('material_volume', length=0.1, width=0.1, height=0.1))
print('Material Volume @ length = 0.1 m, width = 0.4 m, height = 0.7 m: ', net.evaluate('material_volume', length=0.1, width=0.4, height=0.7))
print('Material Volume @ length = 0.5 m, width = 0.4 m, height = 0.7 m: ', net.evaluate('material_volume', length=0.5, width=0.4, height=0.7))
print('Material Volume @ length = 0.6 m, width = 0.2 m, height = 0.3 m: ', net.evaluate('material_volume', length=0.6, width=0.2, height=0.3))
print('Material Volume @ length = 0.8 m, width = 0.3 m, height = 0.1 m: ', net.evaluate('material_volume', length=0.8, width=0.3, height=0.1))

# Output some learned center-of-gravity z-coordinates for random geometries
print('Center of Gravity Z @ length = 0.1 m, width = 0.1 m, height = 0.1 m: ', net.evaluate('cg_z', length=0.1, width=0.1, height=0.1))
print('Center of Gravity Z @ length = 0.1 m, width = 0.4 m, height = 0.7 m: ', net.evaluate('cg_z', length=0.1, width=0.4, height=0.7))
print('Center of Gravity Z @ length = 0.5 m, width = 0.4 m, height = 0.7 m: ', net.evaluate('cg_z', length=0.5, width=0.4, height=0.7))
print('Center of Gravity Z @ length = 0.6 m, width = 0.2 m, height = 0.3 m: ', net.evaluate('cg_z', length=0.6, width=0.2, height=0.3))
print('Center of Gravity Z @ length = 0.8 m, width = 0.3 m, height = 0.1 m: ', net.evaluate('cg_z', length=0.7, width=0.3, height=0.1))
