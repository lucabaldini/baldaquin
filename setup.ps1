
# $BALDAQUIN_ROOT points to the folder where the setup file lives.
$env:BALDAQUIN_ROOT = Get-Location

# Prepend $BALDAQUIN_ROOT to the $PYTHONPATH environmental variable.
$env:PYTHONPATH = "$env:BALDAQUIN_ROOT;$env:PYTHONPATH"

# Print the new environment for verification.
Write-Output "BALDAQUIN_ROOT: $env:BALDAQUIN_ROOT"
Write-Output "Updated PYTHONPATH: $env:PYTHONPATH"
