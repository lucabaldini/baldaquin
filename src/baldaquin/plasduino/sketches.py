# Copyright (C) 2024 the baldaquin team.
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Plasduino sketch information.
"""

from pathlib import Path

from baldaquin.env import BALDAQUIN_SOURCE
from baldaquin.plasduino import PROJECT_NAME

PLASDUINO_SKETCH_ROOT = BALDAQUIN_SOURCE / PROJECT_NAME / "sketches"

# Dictionary holding the correspondence between the (sketch_id, sketch_version)
# tuple and the name of the actual sketch to be uploaded on the board.
# (This could have been handled in a more sensible way with a hash, but it's too late.)
_PLASDUINO_SKETCH_DICT = {
    (1, 3): "digital_timer.hex",
    (2, 3): "analog_sampling.hex"
}


def sketch_file_path(sketch_id: int, sketch_version: int) -> Path:
    """Return the full file path pointing to the compiled version of a given
    sketch.

    Arguments
    ---------
    sketch_id : int
        The identification number for the sketch.

    sketch_version : int
        The sketch version.

    Returns
    -------
    Path
        The full path to the binary file ready to be uploaded on the board.
    """
    try:
        file_name = _PLASDUINO_SKETCH_DICT[(sketch_id, sketch_version)]
    except KeyError as exc:
        raise RuntimeError(f"No information for sketch {sketch_id} version {sketch_version}") \
            from exc
    return PLASDUINO_SKETCH_ROOT / file_name
