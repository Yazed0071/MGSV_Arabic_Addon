
@echo off
echo Building MGSV_Arabic_xml.exe ...
python -m PyInstaller --onefile --noconsole fix_arabic_xml.py
echo.
echo Build finished. Check the dist folder.
pause
