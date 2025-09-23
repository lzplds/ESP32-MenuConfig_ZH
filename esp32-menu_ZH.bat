@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo ESP32 Menu Configuration Tool Launcher
echo ================================================
echo.

REM Setup variables
set "SCRIPT_DIR=%~dp0"
set "APP_SCRIPT=%SCRIPT_DIR%app\menu_covert.py"
set "PYTHON_FOUND=0"
set "PYTHON_EXE="

echo [Step 1] Checking if target script exists...
if not exist "%APP_SCRIPT%" (
    echo [ERROR] Target script not found: %APP_SCRIPT%
    pause
    exit /b 1
)
echo [SUCCESS] Target script exists: %APP_SCRIPT%
echo.

echo [Step 2] Checking system Python environment...
REM Check if system has python environment
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Found Python environment in system
    python --version
    set "PYTHON_EXE=python"
    set "PYTHON_FOUND=1"
    goto :run_script
) else (
    echo [INFO] Python environment not found in system PATH
)
echo.

echo [Step 3] Searching for Python in IDF tools path...
REM Check IDF_TOOLS_PATH environment variable
if "%IDF_TOOLS_PATH%"=="" (
    echo [WARNING] IDF_TOOLS_PATH environment variable not set
    goto :python_not_found
)

echo [INFO] IDF_TOOLS_PATH: %IDF_TOOLS_PATH%
set "IDF_PYTHON_DIR=%IDF_TOOLS_PATH%\tools\idf-python"

REM Check if idf-python directory exists
if not exist "%IDF_PYTHON_DIR%" (
    echo [WARNING] IDF Python directory does not exist: %IDF_PYTHON_DIR%
    goto :python_not_found
)

echo [INFO] Searching for versions in IDF Python directory: %IDF_PYTHON_DIR%

REM Iterate through all possible Python version directories
for /d %%v in ("%IDF_PYTHON_DIR%\*") do (
    echo [CHECK] Version directory: %%v
    
    REM Check common Python executable paths
    set "PYTHON_CANDIDATES=%%v\python.exe;%%v\Scripts\python.exe;%%v\bin\python.exe"
    
    for %%p in (!PYTHON_CANDIDATES!) do (
        if exist "%%p" (
            echo [TEST] Trying Python: %%p
            "%%p" --version >nul 2>&1
            if !errorlevel! equ 0 (
                echo [SUCCESS] Found working Python: %%p
                "%%p" --version
                set "PYTHON_EXE=%%p"
                set "PYTHON_FOUND=1"
                goto :run_script
            ) else (
                echo [FAILED] Python cannot run properly: %%p
            )
        )
    )
)

REM If standard paths not found try deep search
echo [INFO] Performing deep search...
for /r "%IDF_PYTHON_DIR%" %%f in (python.exe) do (
    if exist "%%f" (
        echo [TEST] Deep search found: %%f
        "%%f" --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo [SUCCESS] Deep search found working Python: %%f
            "%%f" --version
            set "PYTHON_EXE=%%f"
            set "PYTHON_FOUND=1"
            goto :run_script
        )
    )
)

:python_not_found
echo.
echo ================================================
echo [ERROR] No available Python environment found!
echo.
echo Please ensure one of the following conditions is met:
echo 1. Python is included in system PATH
echo 2. IDF_TOOLS_PATH environment variable is set with ESP-IDF Python installed
echo.
echo Current checked paths:
echo - python command in system PATH
echo - %IDF_TOOLS_PATH%\tools\idf-python\*\python.exe
echo ================================================
pause
exit /b 1

:run_script
echo.
echo ================================================
echo [Step 4] Running Python script...
echo Python path: %PYTHON_EXE%
echo Script path: %APP_SCRIPT%
echo ================================================
echo.
echo Starting script execution...
echo.

REM Run target script
"%PYTHON_EXE%" "%APP_SCRIPT%"

REM Check script execution result
if !errorlevel! equ 0 (
    REM Exit directly when script completes successfully without message
    exit /b 0
) else (
    echo.
    echo [ERROR] Script execution failed, exit code: !errorlevel!
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b !errorlevel!
)