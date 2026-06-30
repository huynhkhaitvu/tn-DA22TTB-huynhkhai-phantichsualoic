@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   🚀 KHỞI ĐỘNG HỆ THỐNG PHÂN TÍCH LỖI MÃ C
echo ============================================
echo.

REM Kiểm tra GCC
echo [1] Kiểm tra GCC...
gcc --version >nul 2>&1
if errorlevel 1 (
    echo ❌ GCC không được tìm thấy! Vui lòng cài đặt MinGW-w64
    pause
    exit /b 1
)
echo ✓ GCC đã sẵn sàng

REM Kiểm tra Python
echo [2] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy! Vui lòng cài đặt Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python đã sẵn sàng

REM Kiểm tra .env
echo [3] Kiểm tra Gemini API Key...
if not exist "backend\.env" (
    echo ❌ File backend\.env không tồn tại!
    echo Vui lòng tạo file với nội dung:
    echo GEMINI_API_KEY=your-api-key-here
    echo FLASK_ENV=development
    pause
    exit /b 1
)
echo ✓ File .env tồn tại

REM Khởi động Backend
echo.
echo [4] Khởi động Backend (Flask)...
echo ⏳ Backend sẽ mở trong terminal mới...
start cmd /k "cd /d %cd%\backend && python app.py"

REM Chờ backend khởi động
echo.
echo [5] Chờ backend khởi động (3 giây)...
timeout /t 3 /nobreak

REM Mở Frontend
echo [6] Mở Frontend trong trình duyệt...
for /f %%i in ('cd') do set current_dir=%%i

REM Thử dùng Live Server từ VS Code extension nếu có
REM Hoặc mở file HTML trực tiếp
cd /d "%current_dir%\frontend"
start "" index.html

echo.
echo ============================================
echo   ✓ HỆ THỐNG ĐÃ KHỞI ĐỘNG
echo ============================================
echo.
echo 📌 CHÚ Ý:
echo   - Backend chạy trên: http://localhost:5000
echo   - Frontend mở trong trình duyệt
echo   - Giữ terminal backend MỞ
echo   - Nếu muốn dừng: Đóng terminal backend
echo.
echo 💡 TỪI ĐẦU:
echo   - Chính: index.html (Phân tích & Biên dịch)
echo   - Học tập: learning.html (Interactive Learning)
echo.
pause
