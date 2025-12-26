# 🔧 CyberNova Advanced Detection - Compatibility Solutions

## 🚨 **"This app can't run on your PC" Error - SOLUTIONS**

### **📋 Quick Fixes (Try in Order):**

#### **1. Run as Administrator**
```
Right-click CyberNova_Advanced_Detection.exe
→ Select "Run as administrator"
→ Click "Yes" when prompted
```

#### **2. Install Microsoft Visual C++ Redistributable**
```
Download from Microsoft:
https://aka.ms/vs/17/release/vc_redist.x64.exe

Install and restart computer
```

#### **3. Compatibility Mode**
```
Right-click CyberNova_Advanced_Detection.exe
→ Properties
→ Compatibility tab
→ Check "Run this program in compatibility mode"
→ Select "Windows 10"
→ Check "Run as administrator"
→ Apply → OK
```

#### **4. Windows Defender Exclusion**
```
Windows Security → Virus & threat protection
→ Manage settings (under Virus & threat protection settings)
→ Add or remove exclusions
→ Add an exclusion → File
→ Select CyberNova_Advanced_Detection.exe
```

#### **5. Move to Different Location**
```
Move the .exe file from Downloads to:
C:\Users\[YourName]\Desktop\
or
C:\Program Files\CyberNova\
```

---

## 🛠️ **Advanced Solutions**

### **System Requirements Check:**
- ✅ Windows 10/11 (64-bit) - **REQUIRED**
- ✅ 4GB RAM minimum
- ✅ 200MB free disk space
- ✅ .NET Framework 4.7.2+

### **If Still Not Working:**

#### **Method 1: Install Missing Dependencies**
```powershell
# Run in PowerShell as Administrator:
winget install Microsoft.VCRedist.2015+.x64
winget install Microsoft.DotNet.Framework.DeveloperPack_4
```

#### **Method 2: System File Check**
```cmd
# Run in Command Prompt as Administrator:
sfc /scannow
DISM /Online /Cleanup-Image /RestoreHealth
```

#### **Method 3: Windows Update**
```
Settings → Update & Security → Windows Update
→ Check for updates
→ Install all available updates
→ Restart computer
```

---

## 🔍 **Diagnostic Steps**

### **Check System Architecture:**
```cmd
# Run in Command Prompt:
echo %PROCESSOR_ARCHITECTURE%
# Should show: AMD64 (for 64-bit)
```

### **Check Windows Version:**
```cmd
# Run in Command Prompt:
winver
# Should show: Windows 10 build 19041+ or Windows 11
```

### **Check .NET Framework:**
```cmd
# Run in Command Prompt:
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" /v Release
# Should show: 461808 or higher
```

---

## 📱 **Alternative Installation Methods**

### **Method 1: Portable Version**
1. Create folder: `C:\CyberNova\`
2. Copy executable to this folder
3. Run from this location

### **Method 2: Compatibility Wrapper**
Create a batch file `run_cybernova.bat`:
```batch
@echo off
cd /d "%~dp0"
echo Starting CyberNova Advanced Detection...
echo.
echo If you see errors, try running as Administrator
echo.
pause
CyberNova_Advanced_Detection.exe
pause
```

### **Method 3: PowerShell Launcher**
Create `launch_cybernova.ps1`:
```powershell
# PowerShell Launcher for CyberNova
Write-Host "CyberNova Advanced Detection Launcher" -ForegroundColor Green
Write-Host "Checking system compatibility..." -ForegroundColor Yellow

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
    Start-Process PowerShell -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
    exit
}

# Launch the application
Write-Host "Starting CyberNova Advanced Detection..." -ForegroundColor Green
Start-Process ".\CyberNova_Advanced_Detection.exe" -Wait
```

---

## 🆘 **Emergency Fallback**

### **If Nothing Works - Rebuild Options:**

#### **Option 1: 32-bit Version**
```bash
# For older systems, build 32-bit version:
pyinstaller --onefile --windowed --target-architecture=i386 main.py
```

#### **Option 2: Console Version**
```bash
# Build with console for debugging:
pyinstaller --onefile --console main.py
```

#### **Option 3: Directory Distribution**
```bash
# Build as directory (not single file):
pyinstaller --windowed --onedir main.py
```

---

## 📞 **Support Information**

### **Common Error Codes:**
- **0xc000007b** → Install Visual C++ Redistributable
- **0xc0000142** → Run as Administrator
- **0x80070005** → Antivirus blocking (add exclusion)
- **Missing DLL** → Install Windows Updates

### **System Information to Collect:**
```cmd
# Run these commands and share output:
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
wmic os get caption,version,buildnumber,osarchitecture
```

### **Contact Support:**
If all solutions fail, provide:
1. Windows version (from `winver`)
2. System architecture (32/64-bit)
3. Antivirus software name
4. Error message screenshot
5. System information output

---

## ✅ **Success Indicators**

### **Application Should:**
- ✅ Start within 3-5 seconds
- ✅ Show login screen with blue theme
- ✅ Display "CyberNova Advanced Detection" title
- ✅ Allow user registration/login
- ✅ No error dialogs on startup

### **If Working Correctly:**
```
🟢 Login screen appears
🟢 No Windows error dialogs
🟢 Application responds to clicks
🟢 Can create user account
🟢 Dashboard loads after login
```

---

**Last Updated:** December 10, 2024  
**Compatibility Tested:** Windows 10/11 (64-bit)  
**Build Version:** CyberNova Advanced Detection v2.1