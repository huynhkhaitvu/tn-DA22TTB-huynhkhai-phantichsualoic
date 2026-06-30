@echo off
chcp 65001 >nul
echo.
echo ╔═════════════════════════════════════════╗
echo ║  📋 HƯỚNG DẪN CẤU HÌNH GEMINI API KEY  ║
echo ╚═════════════════════════════════════════╝
echo.

echo Bước 1: Vào https://aistudio.google.com/app/apikey
echo.
echo Bước 2: Bấm "Create API key" nếu chưa có
echo.
echo Bước 3: Copy API key (dạng: AIzaSyD...)
echo.
echo Bước 4: Tạo file backend\.env với nội dung:
echo.
echo ─────────────────────────────────────────────
echo GEMINI_API_KEY=paste-your-api-key-here
echo FLASK_ENV=development
echo FLASK_DEBUG=True
echo ─────────────────────────────────────────────
echo.
echo Bước 5: Lưu file
echo.
echo Bước 6: Chạy RUN.bat
echo.
pause
