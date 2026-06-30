@echo off
chcp 65001 >nul
cls
echo.
echo ╔═════════════════════════════════════════╗
echo ║  🔍 KIỂM TRA GCC (C Compiler)          ║
echo ╚═════════════════════════════════════════╝
echo.

echo [1] Kiểm tra GCC...
echo.

gcc --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo ❌ GCC KHÔNG TÌM THẤY!
    echo.
    echo Giải pháp:
    echo ──────────────────────────────────
    echo 1. Cài đặt MinGW-w64 từ:
    echo    https://www.mingw-w64.org/
    echo.
    echo 2. Hoặc dùng Chocolatey:
    echo    choco install mingw
    echo.
    echo 3. Thêm vào PATH:
    echo    • Chuột phải "This PC" → Properties
    echo    • Advanced system settings
    echo    • Environment Variables
    echo    • Path → New
    echo    • Thêm: C:\Program Files\mingw-w64\x86_64-...\bin
    echo.
    echo 4. Restart Windows hoặc reopen PowerShell
    echo.
    echo 5. Chạy lại file này để kiểm tra
    echo ──────────────────────────────────
    echo.
    echo Bấm phím bất kỳ để thoát...
    pause >nul
    exit /b 1
) else (
    color 0A
    echo ✓ GCC đã cài đặt!
    echo.
    gcc --version
    echo.
    echo ✓ Tất cả OK! Có thể chạy RUN.bat
    echo.
    pause
)
