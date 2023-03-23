# Copyright (C) 2023 the baldaquin team.
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

"""Mock project.
"""

from baldaquin import setup_project, _create_folder


MOCK_PROJECT_NAME = 'mock'

MOCK_CONFIG, MOCK_DATA = setup_project(MOCK_PROJECT_NAME)

# We should evaluate if the following makes sense and should be propagated
# to all the projects.
MOCK_APP_CONFIG = MOCK_CONFIG / 'apps'
_create_folder(MOCK_APP_CONFIG)

def user_application_config_file_path(application_name : str):
    """
    """
    file_name = f'{application_name}.cfg'
    return MOCK_APP_CONFIG / file_name
