@ECHO OFF
REM See this stackoverflow question
REM http:\\stackoverflow.com\questions\3827567\how-to-get-the-path-of-the-batch-script-in-windows
REM for the magic in this command
SET WIN_SETUP_DIR=%~dp0
SET SETUP_DIR=%WIN_SETUP_DIR:\=/%

SET BALDAQUIN_ROOT=%SETUP_DIR:~0,-1%
ECHO "BALDAQUIN_ROOT set to " %BALDAQUIN_ROOT%

SET PYTHONPATH=%BALDAQUIN_ROOT%;%PYTHONPATH%
ECHO "PYTHONPATH set to " %PYTHONPATH%
