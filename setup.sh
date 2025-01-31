#!/bin/bash

# See this stackoverflow question
# http://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
# for the magic in this command
#
SETUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# $BALDAQUIN_ROOT points to the folder where the setup file lives.
export BALDAQUIN_ROOT=$SETUP_DIR

# Prepend $BALDAQUIN_ROOT to the $PYTHONPATH environmental variable.
export PYTHONPATH=$BALDAQUIN_ROOT:$PYTHONPATH

# Print the new environment for verification.
echo "BALDAQUIN_ROOT ->" $BALDAQUIN_ROOT
echo "PYTHONPATH ->" $PYTHONPATH
