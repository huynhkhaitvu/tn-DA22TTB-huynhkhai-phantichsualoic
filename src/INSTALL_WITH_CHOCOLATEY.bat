@echo off
chcp 65001 >nul
cls
color 0F
echo.
echo ╔════════════════════════════════════════════════╗
echo ║  ⚡ HƯỚNG DẪN CÀI GCC BẰNG CHOCOLATEY          ║
echo ╚════════════════════════════════════════════════╝
echo.

echo BƯỚC 1️⃣ : Kiểm tra Chocolatey
echo ────────────────────────────────
choco --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo ❌ Chocolatey chưa cài!
    echo.
    echo Vui lòng cài Chocolatey:
    echo.
    echo 1. Mở PowerShell as ADMINISTRATOR
    echo 2. Copy-paste lệnh này:
    echo.
    echo Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    echo.
    echo 3. Bấm Enter, chờ cài xong
    echo 4. Restart PowerShell
    echo 5. Chạy lại file này
    echo.
    echo ═════════════════════════════════════════════
    echo Hoặc xem hướng dẫn tại:
    echo https://docs.chocolatey.org/en-us/choco/setup
    echo ═════════════════════════════════════════════
    echo.
    pause
    exit /b 1
)

color 0A
echo ✓ Chocolatey sẵn sàng
echo.

echo BƯỚC 2️⃣: Cài MinGW-w64 (GCC)
echo ────────────────────────────────
echo ⏳ Đang cài... (chờ 2-5 phút)
echo.

choco install mingw -y

echo.
if errorlevel 0 (
    color 0A
    echo ✓ Cài xong!
) else (
    color 4F
    echo ❌ Lỗi cài đặt
    echo.
    echo Thử lại hoặc xem:
    echo INSTALL_GCC_GUIDE.txt
    echo.
    pause
    exit /b 1
)

echo.
echo BƯỚC 3️⃣ : Restart PowerShell
echo ────────────────────────────────
echo ⚠️  QUAN TRỌNG:
echo   • Đóng PowerShell hiện tại
echo   • Mở PowerShell MỚI
echo   • Test: gcc --version
echo.

pause
