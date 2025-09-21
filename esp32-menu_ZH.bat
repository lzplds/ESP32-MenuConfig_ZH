@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 使用CMD的/C参数来禁用Ctrl+C确认
if "%1" neq "NOCRLF" (
    cmd /c ""%~f0" NOCRLF %*"
    exit /b %errorlevel%
)

echo [INFO] ESP32 Menu ZH 启动脚本
echo [INFO] 当前工作目录: %CD%
echo [INFO] 脚本目录: %~dp0
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"
echo [INFO] 已切换到脚本目录: %CD%
echo.

:: 定义目标Python脚本路径
set "TARGET_SCRIPT=app\menu_covert.py"
echo [INFO] 目标脚本: %TARGET_SCRIPT%

:: 检查目标脚本是否存在
if not exist "%TARGET_SCRIPT%" (
    echo [ERROR] 目标脚本不存在: %TARGET_SCRIPT%
    echo [ERROR] 请确认文件路径是否正确
    pause
    exit /b 1
)
echo [INFO] 目标脚本存在，继续执行
echo.

:: 第一步：检查系统是否有python3解释器
echo [INFO] 步骤1: 检查系统是否安装python3解释器
set "PYTHON_EXE="

:: 尝试python3命令
echo [INFO] 正在检查 python3 命令...
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] 找到 python3 解释器
    set "PYTHON_EXE=python3"
    python3 --version
    goto :run_script
) else (
    echo [INFO] python3 命令不可用
)

:: 尝试python命令
echo [INFO] 正在检查 python 命令...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [INFO] 找到 python 解释器，检查版本...
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
        echo [INFO] Python版本: %%v
        echo %%v | findstr "^3\." >nul
        if !errorlevel! equ 0 (
            echo [SUCCESS] 找到 Python 3.x 解释器
            set "PYTHON_EXE=python"
            goto :run_script
        ) else (
            echo [INFO] Python版本不是3.x，继续查找
        )
    )
) else (
    echo [INFO] python 命令不可用
)

echo [INFO] 系统中未找到可用的Python 3解释器
echo.

:: 第二步：在IDF_TOOLS_PATH中查找Python
echo [INFO] 步骤2: 在IDF_TOOLS_PATH中查找Python解释器

if "%IDF_TOOLS_PATH%"=="" (
    echo [ERROR] 环境变量 IDF_TOOLS_PATH 未设置
    echo [ERROR] 无法继续查找ESP-IDF Python解释器
    pause
    exit /b 1
)

echo [INFO] IDF_TOOLS_PATH: %IDF_TOOLS_PATH%
set "IDF_PYTHON_PATH=%IDF_TOOLS_PATH%\tools\idf-python"
echo [INFO] 搜索路径: %IDF_PYTHON_PATH%

if not exist "%IDF_PYTHON_PATH%" (
    echo [ERROR] IDF Python工具目录不存在: %IDF_PYTHON_PATH%
    pause
    exit /b 1
)

echo [INFO] 正在搜索可用的Python版本目录...
set "FOUND_VERSION="
for /d %%d in ("%IDF_PYTHON_PATH%\*") do (
    set "VERSION_DIR=%%~nxd"
    echo [INFO] 检查版本目录: !VERSION_DIR!
    
    :: 检查是否为版本号格式 (包含数字和点)
    echo !VERSION_DIR! | findstr "[0-9]\.[0-9]" >nul
    if !errorlevel! equ 0 (
        set "PYTHON_PATH=%%d\python.exe"
        echo [INFO] 检查Python解释器: !PYTHON_PATH!
        
        if exist "!PYTHON_PATH!" (
            echo [SUCCESS] 找到Python解释器: !PYTHON_PATH!
            "!PYTHON_PATH!" --version
            set "PYTHON_EXE=!PYTHON_PATH!"
            set "FOUND_VERSION=!VERSION_DIR!"
            goto :run_script
        ) else (
            echo [INFO] Python解释器不存在: !PYTHON_PATH!
        )
    ) else (
        echo [INFO] 跳过非版本目录: !VERSION_DIR!
    )
)

if "%FOUND_VERSION%"=="" (
    echo [ERROR] 在IDF_TOOLS_PATH中未找到可用的Python解释器
    echo [ERROR] 已搜索路径: %IDF_PYTHON_PATH%
    pause
    exit /b 1
)

:run_script
echo.
echo [INFO] ========================================
echo [INFO] 准备运行目标脚本
echo [INFO] Python解释器: %PYTHON_EXE%
echo [INFO] 目标脚本: %TARGET_SCRIPT%
echo [INFO] ========================================
echo.
echo [INFO] 开始执行Python脚本...

:: 运行Python脚本，直接在当前窗口执行
echo [INFO] 正在执行: "%PYTHON_EXE%" "%TARGET_SCRIPT%"
"%PYTHON_EXE%" "%TARGET_SCRIPT%"

:: Python脚本执行完成，直接退出
exit /b %errorlevel%