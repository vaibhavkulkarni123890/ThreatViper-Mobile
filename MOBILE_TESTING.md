# How to Test on Mobile (Without APK)

You can test the app on your phone **instantly** without building an APK file. This connects your phone directly to your PC.

## Method 1: The "Flet" App (Recommended)
This makes it look exactly like a real app (no browser bar).

1.  **On your Android Phone**:
    *   Open **Play Store**.
    *   Search for **"Flet"** (by Appveyor Systems).
    *   Install it.

2.  **On your PC**:
    *   Open Terminal in `CyberNovaMobile/`.
    *   Run: `python main.py`
    *   Example Output: `Running Flet App... Open http://192.168.1.5:8550`

3.  **Connect**:
    *   Open the **Flet App** on your phone.
    *   Tap the **"+"** button.
    *   Enter the URL from your PC (e.g., `http://192.168.1.5:8550`).
    *   Tap **"Add"** and then tap the Project.

**Result**: The app runs natively on your phone!

---

## Method 2: Mobile Browser (Easiest)
If you don't want to install the Flet app yet.

1.  **On your PC**:
    *   Run: `python main.py`

2.  **On your Phone**:
    *   Make sure you are on the **Same Wi-Fi** as your PC.
    *   Open Chrome / Safari.
    *   Type IP address: `http://192.168.1.5:8550` (Replace with your actual IP).

**Result**: The app runs in your browser.
