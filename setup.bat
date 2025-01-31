@ECHO OFF

:: $BALDAQUIN_ROOT points to the folder where the setup file lives.
set "BALDAQUIN_ROOT=%CD%"

:: Prepend $BALDAQUIN_ROOT to the $PYTHONPATH environmental variable.
set "PYTHONPATH=%BALDAQUIN_ROOT%;%PYTHONPATH%"

:: Print the new environment for verification.
echo BALDAQUIN_ROOT -> %BALDAQUIN_ROOT%
echo PYTHONPATH -> %PYTHONPATH%
