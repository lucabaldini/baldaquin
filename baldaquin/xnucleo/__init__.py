# Copyright (C) 2025 the baldaquin team.
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

"""xnucleo project.
"""

from pathlib import Path

from baldaquin import setup_project


PROJECT_NAME = 'xnucleo'

XNUCLEO_CONFIG, XNUCLEO_APP_CONFIG, XNUCLEO_DATA = setup_project(PROJECT_NAME)

XNUCLEO_ROOT = Path(__file__).parent

XNUCLEO_SKETCHES = XNUCLEO_ROOT / 'sketches'
