@ECHO OFF

:: Get the current directory (PWD)
set "BALDAQUIN_ROOT=%CD%"

:: Prepend the current directory to PYTHONPATH
set "PYTHONPATH=%BALDAQUIN_ROOT%;%PYTHONPATH%"

:: Print the new PYTHONPATH for verification
echo BALDAQUIN_ROOT: %BALDAQUIN_ROOT%
echo Updated PYTHONPATH: %PYTHONPATH%