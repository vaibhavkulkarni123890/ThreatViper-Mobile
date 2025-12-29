@echo off
echo ==========================================
echo      THREATVIPER SECURITY - APK BUILDER
echo ==========================================
echo.
echo 1. Checking Environment...
echo.
call flutter doctor
if %errorlevel% neq 0 (
    echo [ERROR] Flutter is not installed or configured!
    echo Please install Flutter and Android Studio to build APKs.
    pause
    exit /b
)

echo.
echo 2. Installing Python Dependencies...
pip install -r requirements.txt
pip install flet

echo.
echo 3. Building APK...
echo This process may take a few minutes...
flet build apk --project=ThreatViper --verbose

echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] APK Built Successfully!
    echo Check the 'build/apk' folder.
) else (
    echo [FAILURE] Build Failed. Check the logs above.
)
pause
