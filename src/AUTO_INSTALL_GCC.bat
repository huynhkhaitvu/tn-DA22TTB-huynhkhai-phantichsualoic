@echo off
chcp 65001 >nul
cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║  📥 CÀI ĐẶT GCC TỰ ĐỘNG (MinGW-w64)         ║
echo ╚═══════════════════════════════════════════════╝
echo.

REM Kiểm tra admin rights
net session >nul 2>&1
if errorlevel 1 (
    color 4F
    echo ❌ LỖI: Cần chạy "Run as Administrator"
    echo.
    echo Vui lòng:
    echo 1. Chuột phải file này
    echo 2. Chọn "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1] Kiểm tra Chocolatey...
choco --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo ❌ Chocolatey không cài!
    echo.
    echo Cài Chocolatey từ: https://chocolatey.org/install
    echo.
    echo Hoặc chạy PowerShell as Admin:
    echo Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    echo.
    echo Sau đó: Chạy lại file này
    echo.
    pause
    exit /b 1
)

echo ✓ Chocolatey sẵn sàng
echo.

echo [2] Cài GCC (MinGW-w64)...
echo ⏳ Đang cài... (chờ 2-5 phút)
echo.

choco install mingw -y

if errorlevel 0 (
    color 0A
    echo.
    echo ✓ Cài xong!
    echo.
    echo [3] Thêm vào PATH...
) else (
    color 4F
    echo.
    echo ❌ Lỗi cài đặt!
    echo.
    pause
    exit /b 1
)

REM Tìm GCC path
for /f "delims=" %%i in ('where gcc 2^>nul') do (
    set GCC_PATH=%%i
)

if defined GCC_PATH (
    echo ✓ GCC tìm thấy: %GCC_PATH%
    echo.
    
    echo [4] Kiểm tra...
    gcc --version
    
    echo.
    echo ✓ GCC đã cài xong!
    echo.
    echo ⚠️  Restart PowerShell để PATH cập nhật
    echo.
) else (
    echo ⚠️  GCC chưa trong PATH
    echo.
    echo Vui lòng restart Windows hoặc dùng:
    echo ADD_GCC_TO_PATH.bat
)

echo.
echo Bấm phím bất kỳ để thoát...
pause >nul
