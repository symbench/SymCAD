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
from . import FixedPart

class Garmin15HGpsReceiver(FixedPart):
   """Model representing a Garmin 15H GPS Receiver.

   By default, the part is oriented in the following way:

   ![Garmin15HGpsReceiver](https://symbench.github.io/SymCAD/images/Garmin15HGpsReceiver.png)
   """

   # Constructor ----------------------------------------------------------------------------------

   def __init__(self, identifier: str) -> None:
      """Initializes the Garmin 15H GPS Receiver fixed-geometry part.

      Parameters
      ----------
      identifier : `str`
         Unique identifying name for the object.
      """
      super().__init__(identifier, 'radios/Garmin-15H-GPS-Receiver.FCStd', 1107.106)
      self.set_unexposed()
