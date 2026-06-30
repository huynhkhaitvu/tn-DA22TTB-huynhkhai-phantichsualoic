@REM Cách 1: Double-click file này để mở hệ thống
@REM Hoặc: chạy: START_SYSTEM.bat

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════╗
echo ║  🚀 KHỞI ĐỘNG HỆ THỐNG PHÂN TÍCH LỖI  ║
echo ╚════════════════════════════════════════╝
echo.

REM Lấy đường dẫn script
set SCRIPT_DIR=%~dp0

REM Kiểm tra GCC
echo [1/4] Kiểm tra GCC...
gcc --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo ❌ GCC KHÔNG TÌM THẤY!
    echo.
    echo Giải pháp:
    echo   - Tải MinGW-w64 từ: https://www.mingw-w64.org/
    echo   - Cài đặt và thêm vào PATH
    echo.
    pause
    exit /b 1
)
echo ✓ GCC ready
color 0A

REM Kiểm tra Python
echo [2/4] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo ❌ PYTHON KHÔNG TÌM THẤY!
    echo.
    echo Giải pháp:
    echo   - Tải Python từ: https://www.python.org/
    echo   - Chọn "Add Python to PATH" khi cài
    echo.
    pause
    exit /b 1
)
echo ✓ Python ready

REM Kiểm tra .env
echo [3/4] Kiểm tra Gemini API Key...
if not exist "%SCRIPT_DIR%backend\.env" (
    color 4F
    echo.
    echo ❌ FILE .env KHÔNG TỌN TẠI!
    echo.
    echo Vui lòng tạo file: backend\.env
    echo Nội dung:
    echo   GEMINI_API_KEY=your-api-key-here
    echo   FLASK_ENV=development
    echo.
    echo Lấy API Key từ: https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)
echo ✓ API Key configured

REM Kiểm tra requirements.txt
echo [4/4] Kiểm tra Python packages...
if not exist "%SCRIPT_DIR%backend\requirements.txt" (
    echo ⚠️  requirements.txt không tìm thấy, tạo mới...
    (
        echo flask
        echo flask-cors
        echo python-dotenv
        echo requests
    ) > "%SCRIPT_DIR%backend\requirements.txt"
)
echo ✓ Requirements ready

REM Chuẩn bị
color 0B
echo.
echo ════════════════════════════════════════
echo   ✓ Tất cả kiểm tra thành công!
echo ════════════════════════════════════════
echo.
echo 🔄 KHỞI ĐỘNG:
echo   - Backend (Flask) sẽ mở trong terminal
echo   - Frontend (Browser) sẽ mở tự động
echo.

REM Khởi động Backend
color 0E
echo ⏳ Khởi động Backend...
start cmd /k "cd /d %SCRIPT_DIR%backend && python app.py"

REM Chờ backend khởi động
timeout /t 4 /nobreak

REM Mở Frontend
color 0B
echo ✓ Mở Frontend...

REM Cách 1: Mở file trực tiếp (Windows sẽ dùng trình duyệt mặc định)
start "" "%SCRIPT_DIR%frontend\index.html"

REM Cách 2 (Nếu Cách 1 không hoạt động, bỏ comment):
REM start http://localhost:5500/frontend/index.html

echo.
echo ════════════════════════════════════════
echo   ✓✓✓ HỆ THỐNG KHỞI ĐỘNG THÀNH CÔNG! ✓✓✓
echo ════════════════════════════════════════
echo.
echo 📌 GIAO DIỆN:
echo   - index.html (Phân tích code)
echo   - learning.html (Interactive Learning)
echo.
echo ⚠️  GIỮ TERMINAL BACKEND MỞ!
echo.
echo 🛑 Để DỪNG hệ thống: Đóng terminal Backend
echo.
timeout /t 5
