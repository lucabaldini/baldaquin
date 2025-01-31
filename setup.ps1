# Get the current directory (PWD)
$env:BALDAQUIN_ROOT = Get-Location

# Prepend it to the PYTHONPATH environment variable
$env:PYTHONPATH = "$env:BALDAQUIN_ROOT;$env:PYTHONPATH"

# Print the updated PYTHONPATH
Write-Output "BALDAQUIN_ROOT: $env:BALDAQUIN_ROOT"
Write-Output "Updated PYTHONPATH: $env:PYTHONPATH"
