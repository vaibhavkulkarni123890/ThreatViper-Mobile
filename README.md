# ThreatViper Mobile Security 🛡️

**Next-Gen Android Security Application** focused on Real-time Protection and Strict Installation Monitoring.

![Dashboard Screenshot](/uploaded_image_1765040432068.png)

## 🚀 Features

### 1. 🛡️ Real-time Behavior Shield
- **24/7 Monitoring**: Automatically watches `Downloads`, `Bluetooth`, and `Documents` folders.
- **Strict APK Policy**: instantly **BLOCKS & QUARANTINES** any unauthorized APK installer using heuristics.
- **Zero-Trust**: Only allows verified updates matching the `threatviper` signature.

### 2. 🕵️‍♂️ Smart Scanner
- **Privacy First**: Scans your file system for hidden threats without uploading your data.
- **Auto-Quarantine**: Threats are moved to a secure `.quarantine` vault and locked.

### 3. 🔐 Secure Authentication
- **Secure Cloud**: All scan history and user accounts are stored securely in Appwrite Cloud. No sensitive scan data is stored locally.
- **Encryption**: Military-grade `bcrypt` password hashing.

### 4. ⚡ Performance
- **Passive Monitoring**: Uses virtually **0% CPU** by utilizing efficient file-system listeners instead of constant polling.

## 📥 Installation

### Method 1: Download APK
1.  Check the `Releases` tab.
2.  Download `app-release.apk`.
3.  Install on your Android device (Allow Unknown Sources).

### Method 2: Build from Source
**Requirements:**
- Flutter SDK 3.16+
- Python 3.10+

```bash
# Clone
git clone https://github.com/YourRepo/ThreatViper.git
cd ThreatViper/ThreatViperMobile

# Build
flet build apk --project threatviper_mobile
```

## 📸 Screenshots

| Login | Dashboard (Secure) | Shield Active |
|-------|-----------|---------------|
| ![Login](/uploaded_image_0_1765093040201.jpg) | ![Dash](/uploaded_image_1_1765093040201.jpg) | ![Shield](/uploaded_image_2_1765093040201.jpg) |

### 🛡️ Threat Detection & History
| Threat Blocked (Strict Mode) | Scan History |
|------------------------------|--------------|
| ![Blocked](/uploaded_image_3_1765093040201.jpg) | ![History](/uploaded_image_4_1765093040201.jpg) |

---
*Built with Flet & Python.*
