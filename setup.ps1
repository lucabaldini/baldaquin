# Get the current directory (PWD)
$CURRENT_DIR = Get-Location

# Prepend it to the PYTHONPATH environment variable
$env:PYTHONPATH = "$CURRENT_DIR;$env:PYTHONPATH"

# Print the updated PYTHONPATH
Write-Output "Updated PYTHONPATH: $env:PYTHONPATH"
