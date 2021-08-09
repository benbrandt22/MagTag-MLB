# Copies any new/changed files to the MagTag. This script assumes the MagTag shows up as drive "D:\"
robocopy $PSScriptRoot/src 'D:\' /v /e