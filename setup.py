import platform, re
from pathlib import Path
from setuptools import setup

VERSION = re.search(r'__version__ = \'(.+?)\'',
                    (Path(__file__).parent / "src" / "symcad" / "__init__.py").read_text("utf8"))\
          .group(1)

install_deps = []
with open('requirements.txt') as file:
   for line in file:
      if 'platform_system' in line:
         if (line.split('platform_system==\'')[1].split('\'')[0] == platform.system()) and \
               (line.split('platform_machine==\'')[1].split('\'')[0] == platform.machine()):
            install_deps.append(line.split(';')[0])
      else:
         install_deps.append(line)

setup(
   version=VERSION,
   install_requires=install_deps
)
