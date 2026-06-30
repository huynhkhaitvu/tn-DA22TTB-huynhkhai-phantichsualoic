@echo off
chcp 65001 >nul
cls
echo.
echo ╔═════════════════════════════════════════╗
echo ║  🔧 THÊM GCC VÀO PATH (Tự động)        ║
echo ╚═════════════════════════════════════════╝
echo.

echo [1] Kiểm tra GCC...
gcc --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo ❌ GCC không tìm thấy!
    echo.
    echo Vui lòng cài đặt MinGW-w64 trước:
    echo https://www.mingw-w64.org/
    echo.
    pause
    exit /b 1
)

echo ✓ GCC tìm thấy!
echo.
echo [2] Tìm đường dẫn GCC...

REM Lấy đường dẫn GCC
for /f "delims=" %%i in ('where gcc') do (
    set GCC_PATH=%%i
)

echo Đường dẫn GCC: %GCC_PATH%
echo.

REM Trích đường dẫn folder từ gcc.exe
for %%F in ("%GCC_PATH%") do set GCC_BIN_DIR=%%~dpF

echo Folder bin: %GCC_BIN_DIR%
echo.

echo [3] Thêm vào PATH...
echo.

REM Kiểm tra xem đã có trong PATH chưa
echo %PATH% | findstr /I "%GCC_BIN_DIR%" >nul
if errorlevel 1 (
    echo ⏳ Thêm %GCC_BIN_DIR% vào PATH...
    setx PATH "%PATH%;%GCC_BIN_DIR%"
    echo.
    echo ✓ Đã thêm vào PATH!
    echo.
    echo ⚠️  QUAN TRỌNG:
    echo    - Bạn cần RESTART PowerShell hoặc Terminal
    echo    - Hoặc restart Windows để PATH cập nhật
    echo.
    echo [4] Kiểm tra kết quả...
) else (
    echo ✓ GCC đã trong PATH!
)

echo.
echo Chạy lệnh kiểm tra:
echo   gcc --version
echo.
pause
