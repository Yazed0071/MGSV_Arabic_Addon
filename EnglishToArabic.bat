@echo off
setlocal enabledelayedexpansion

:: Start in the folder where this script is located
pushd "%~dp0"

:: Recursively process files with "eng" in the name
for /r %%f in (*eng*) do (
    set "fullpath=%%f"
    set "filename=%%~nxf"
    set "newname=!filename:eng=ara!"
    set "folder=%%~dpf"
    ren "%%f" "!newname!"
)

echo Renaming completed in all subdirectories.
pause
