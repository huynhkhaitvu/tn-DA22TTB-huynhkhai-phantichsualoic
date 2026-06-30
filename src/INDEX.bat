@echo off
REM INDEX.bat - Mở hệ thống bằng nhấp đúp file INDEX
REM Chức năng: Khởi động backend + mở landing page

setlocal enabledelayedexpansion

REM Lấy thư mục hiện tại
set CURRENT_DIR=%~dp0
set SCRIPT_DIR=%CURRENT_DIR%

REM Mở file INDEX.html từ thư mục hiện tại
start file:///%SCRIPT_DIR%INDEX.html

REM Chạy RUN.bat để khởi động backend
call "%SCRIPT_DIR%RUN.bat"

endlocal
pause
