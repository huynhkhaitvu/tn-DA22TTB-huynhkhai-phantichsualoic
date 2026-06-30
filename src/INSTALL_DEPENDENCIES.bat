@echo off
chcp 65001 >nul
echo.
echo ╔═════════════════════════════════════════╗
echo ║  📦 CÀI ĐẶT PYTHON PACKAGES            ║
echo ╚═════════════════════════════════════════╝
echo.

echo Kiểm tra Python...
python --version
if errorlevel 1 (
    echo.
    echo ❌ Python không được tìm thấy!
    echo Vui lòng cài đặt Python từ: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Python sẵn sàng
echo.
echo Cài đặt packages từ requirements.txt...
echo.

cd /d "%~dp0backend"
pip install -r requirements.txt

echo.
echo ════════════════════════════════════════
echo ✓ Cài đặt hoàn thành!
echo.
echo Chạy lệnh: RUN.bat
echo ════════════════════════════════════════
echo.
pause
