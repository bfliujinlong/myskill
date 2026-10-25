@echo off
chcp 65001 >nul
echo ============================================
echo 明道云工时核查 - 一键运行
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请安装 Python 3.10+: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip install playwright 2>nul
echo.
echo [2/3] 安装浏览器...
python -m playwright install chromium
echo.
echo [3/3] 启动核查...
echo.

python "%~dp0mingdao_auto_audit.py"

echo.
pause
