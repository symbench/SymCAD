import platform
from setuptools import setup

install_deps = []
with open('requirements.txt') as file:
   for line in file:
      if 'platform_system' in line:
         if (line.split('platform_system==\'')[1].split('\'')[0] == platform.system()) and \
               (line.split('platform_machine==\'')[1].split('\'')[0] == platform.machine()) and \
               (line.split('python_version==\'')[1].split('\'')[0].split('.')[0] == platform.python_version_tuple()[0]) and \
               (line.split('python_version==\'')[1].split('\'')[0].split('.')[1] == platform.python_version_tuple()[1]):
            install_deps.append(line.split(';')[0])
      else:
         install_deps.append(line)

setup(install_requires=install_deps)
