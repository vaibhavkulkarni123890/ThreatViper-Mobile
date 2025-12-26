# How to Build the CyberNova Android App

Building a real Android App (`.apk`) requires some powerful developer tools directly from Google. I have written the code, but your computer needs the "compiler" to turn it into an app.

## Prerequisites (One-Time Setup)

You must install these tools on your Windows machine. This typically takes 15-30 minutes.

### 1. Install Flutter SDK
Flet uses Flutter under the hood.
1.  Download the **Flutter SDK for Windows**: [https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.19.0-stable.zip](https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.19.0-stable.zip)
2.  Extract the zip file to `C:\src\flutter` (Create the folder if it doesn't exist).
3.  Add `C:\src\flutter\bin` to your **System Path** (Search Windows for "Edit environment variables for your account").

### 2. Install Android Studio
This provides the Android SDK tools.
1.  Download & Install **Android Studio**: [https://developer.android.com/studio](https://developer.android.com/studio)
2.  Open Android Studio. Go to **Settings > Languages & Frameworks > Android SDK**.
3.  Ensure "Android SDK Command-line Tools" is checked and installed.

### 3. Verify Setup
Open a new terminal (generic Command Prompt) and run:
```bash
flutter doctor
```
If you see checkmarks, you are ready!

---

## Building the APK

Once the tools above are installed, simply run the script I created for you:

1.  Open Terminal in `CyberNovaMobile` folder.
2.  Run:
    ```bash
    flet build apk
    ```
    *or just double-click `build_apk.bat`*

3.  The output file `app-release.apk` will appear in `build/apk/`.
4.  Copy this file to your phone and install it!
