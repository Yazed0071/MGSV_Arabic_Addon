@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "LOG=%ROOT%replace_log.txt"

echo ==== Run %date% %time% ====>>"%LOG%"
set "foundAny=0"

for %%F in ("%ROOT%*.subp") do (
    set "foundAny=1"
    echo Processing "%%~nxF" ...
    for /r "%ROOT%" %%G in ("%%~nxF") do (
        if /I not "%%~fG"=="%%~fF" if exist "%%~fG" (
            copy /Y "%%~fF" "%%~fG" >nul
            if not errorlevel 1 (
                echo %date% %time% - Replaced: "%%~fG" with "%%~fF">>"%LOG%"
                echo   Replaced: "%%~fG"
            )
        )
    )
)

if "!foundAny!"=="0" (
    echo No .subp files found in "%ROOT%".
) else (
    echo Done. See "%LOG%" for details.
)

endlocal
