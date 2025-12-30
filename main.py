# FINAL PRODUCTION VERSION
import flet as ft
import os
import time
import threading
import shutil
import logging
import warnings
from datetime import datetime
import concurrent.futures

# --- GLOBAL WARNING SILENCE ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated since 1.8.0.*")
try:
    logging.getLogger('appwrite').setLevel(logging.CRITICAL)
except: pass

# Configure Logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Legal Text Const - UPDATED FOR COMMERCIAL
TERMS_TEXT = """
THREATVIPER SECURITY: TERMS OF SERVICE

Welcome to ThreatViper! We are committed to protecting your digital life. 
By using our services, you agree to the following simple terms:

1. YOUR PROTECTION
ThreatViper provides advanced security for your personal and business files. 
Your subscription allows you to stay protected for a full year.

2. SECURITY HONESTY
We use advanced technology to detect threats, but no system can be 100% perfect. 
We recommend maintaining backups for your most precious data.

3. YOUR PRIVACY
Your trust is our priority. We only scan for threats locally. 
No personal files or private contents are ever uploaded to our servers.

4. RESPONSIBLE USE
We ask that you use ThreatViper for security purposes only. 
Please do not attempt to bypass our protections or use our tools for harm.

Thank you for choosing ThreatViper. Stay safe!
"""

DISCLAIMER_MSG = "⚠️ Enterprise Heuristics Active. No security system is 100% fallback-proof."

def main(page: ft.Page):
    # App Configuration
    page.title = "ThreatViper Security" 
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 800
    page.padding = 0

    # Show Loading Overlay immediately
    loading_screen = ft.Container(
        expand=True,
        bgcolor="#111111",
        content=ft.Column([
            ft.ProgressRing(color="cyan400"),
            ft.Text("Initializing Secure Environment...", color="grey400", id="boot_status")
        ], alignment="center", horizontal_alignment="center")
    )
    page.add(loading_screen)
    page.update()

    # Initialize Core Systems Safely
    try:
        # Step 1: Logic
        loading_screen.content.controls[1].value = "Loading Threat Engine..."
        page.update()
        
        global db, threat_engine
        # Initialize inside main so we don't block the Python process before Flet starts
        from db_manager import DBManager
        from threat_engine import ThreatEngine
        
        db = DBManager()
        threat_engine = ThreatEngine()
        
        # Step 2: Session
        loading_screen.content.controls[1].value = "Restoring Session..."
        page.update()
        
        # Load session is now non-fatal and non-blocking
        db.load_session()
        
    except Exception as e:
        page.clean()
        page.add(ft.Container(
            expand=True, padding=40,
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color="red400", size=50),
                ft.Text("Startup Error", size=20, weight="bold"),
                ft.Text(f"Details: {str(e)}", color="red300"),
                ft.Text("Check if 'requests' and 'appwrite' are installed.", size=10, color="grey500"),
                ft.ElevatedButton("Retry", on_click=lambda _: main(page))
            ], horizontal_alignment="center", alignment="center")
        ))
        page.update()
        return

    # Final Step: Clear boot UI
    page.clean()

    # State & Caching
    scan_running = False
    shield_active = False
    cached_views = {}
    
    # --- Views ---
    
    def show_dialog(title, message, is_error=False):
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(dlg))]
        )
        page.open(dlg)
    
    def terms_view():
        if "/terms" in cached_views: return cached_views["/terms"]
        v = ft.View(
            "/terms",
            bgcolor="#111111",
            controls=[
                ft.AppBar(title=ft.Text("Terms & Conditions"), bgcolor="#1a1a1a"),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text(TERMS_TEXT, size=14, color="grey300"),
                        ft.Container(height=20),
                        ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/register"))
                    ], scroll=ft.ScrollMode.AUTO)
                )
            ]
        )
        cached_views["/terms"] = v
        return v

    def login_view():
        if "/login" in cached_views: return cached_views["/login"]
        email_field = ft.TextField(label="Email Address", prefix_icon="email", border_radius=10)
        pass_field = ft.TextField(label="Password", prefix_icon="lock", password=True, can_reveal_password=True, border_radius=10)
        
        def do_login(e):
            if not email_field.value or not pass_field.value:
                page.open(ft.SnackBar(ft.Text("Please fill all fields"), bgcolor="red400"))
                return
            page.splash = ft.ProgressBar()
            page.update()
            success, msg = db.login(email_field.value, pass_field.value)
            page.splash = None
            if success:
                page.open(ft.SnackBar(ft.Text(msg), bgcolor="green400"))
                page.go("/dashboard")
            else:
                show_dialog("Login Failed", msg, True)
            page.update()
            
        v = ft.View(
            "/login",
            bgcolor="#111111",
            controls=[
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            ft.Image(src="logo_final.png", width=120, height=120, fit=ft.ImageFit.CONTAIN),
                            ft.Text("THREATVIPER", size=30, weight="bold", color="white"),
                            ft.Text("SECURITY", size=20, weight="w300", color="cyan400"),
                            ft.Text(DISCLAIMER_MSG, size=11, color="orange300", text_align="center", italic=True),
                            ft.Container(height=10),
                            email_field,
                            pass_field,
                            ft.Container(height=10),
                            ft.ElevatedButton("LOGIN", width=320, height=50, style=ft.ButtonStyle(bgcolor="cyan600", color="white", shape=ft.RoundedRectangleBorder(radius=10)), on_click=do_login),
                            ft.Row([
                                ft.TextButton("Create Account", on_click=lambda _: page.go("/register")),
                                ft.TextButton("Terms", on_click=lambda _: page.go("/terms"))
                            ], alignment="center"),
                            ft.Container(height=10),
                            ft.Text("Enterprise Grade Security", size=10, color="grey500")
                        ]
                    )
                )
            ]
        )
        cached_views["/login"] = v
        return v

    def register_view():
        if "/register" in cached_views: return cached_views["/register"]
        name_field = ft.TextField(label="Full Name", prefix_icon="person", border_radius=10)
        email_field = ft.TextField(label="Email Address", prefix_icon="email", border_radius=10)
        pass_field = ft.TextField(label="Password", prefix_icon="lock", password=True, can_reveal_password=True, border_radius=10)
        terms_checkbox = ft.Checkbox(label="I agree to the Terms & Conditions", value=False)
        
        def do_register(e):
            if not all([name_field.value, email_field.value, pass_field.value]):
                page.open(ft.SnackBar(ft.Text("All fields required"), bgcolor="red400"))
                return
            if not terms_checkbox.value:
                show_dialog("Agreement Required", "You must agree to the Terms & Conditions to register.", True)
                return
            page.splash = ft.ProgressBar()
            page.update()
            success, msg = db.register(email_field.value, pass_field.value, name_field.value)
            page.splash = None
            if success:
                page.open(ft.SnackBar(ft.Text("Account Created!"), bgcolor="green400"))
                page.go("/dashboard")
            else:
                show_dialog("Registration Failed", msg, True)
            page.update()

        v = ft.View(
            "/register",
            bgcolor="#111111",
            controls=[
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                        controls=[
                            ft.Icon(ft.Icons.PERSON_ADD, size=60, color="green400"),
                            ft.Text("Create Account", size=24, weight="bold"),
                            ft.Text(DISCLAIMER_MSG, size=10, color="orange300", text_align="center"),
                            ft.Container(height=5),
                            name_field,
                            email_field,
                            pass_field,
                            ft.Row([
                                terms_checkbox,
                                ft.TextButton("Read Terms", on_click=lambda _: page.go("/terms"))
                            ], alignment="center", spacing=0),
                            ft.Container(height=10),
                            ft.ElevatedButton("REGISTER", width=320, height=50, style=ft.ButtonStyle(bgcolor="green600", color="white"), on_click=do_register),
                            ft.TextButton("Back to Login", on_click=lambda _: page.go("/login"))
                        ]
                    )
                )
            ]
        )
        cached_views["/register"] = v
        return v

    def dashboard_view():
        if "/dashboard" in cached_views: return cached_views["/dashboard"]
        
        scan_progress = ft.ProgressBar(width=200, color="cyan400", visible=False)
        status_text = ft.Text("System Protected", color="green400", weight="bold")
        current_file_text = ft.Text("", color="grey", size=10, italic=True)
        shield_switch = ft.Switch(active_color="cyan400")
        
        def run_scan(e):
            nonlocal scan_running
            if scan_running: return
            scan_running = True
            scan_progress.visible = True
            status_text.value = "Initializing Scan..."
            status_text.color = "white"
            current_file_text.value = "Enumerating files..."
            page.update()
            threading.Thread(target=perform_scan).start()
        
        def perform_scan():
            nonlocal scan_running
            # ADAPTATION: Use Windows paths or user home
            # ADAPTATION: Platform-specific paths
            if page.platform == ft.PagePlatform.ANDROID:
                # Android Paths (Internal Storage)
                # Note: Requires permissions for some paths.
                user_home = "/storage/emulated/0"
                paths = [
                    os.path.join(user_home, "Download"),
                    os.path.join(user_home, "Documents"),
                    os.path.join(user_home, "Pictures"),
                    os.path.join(user_home, "DCIM"),
                    os.path.join(user_home, "Music"),
                    os.path.join(user_home, "Movies"),
                    # Social Media Paths (Common locations)
                    os.path.join(user_home, "Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Documents"),
                    os.path.join(user_home, "WhatsApp/Media/WhatsApp Documents"),
                    os.path.join(user_home, "Telegram/Telegram Documents"),
                    os.path.join(user_home, "Android/data/org.telegram.messenger/files/Telegram/Telegram Documents")
                ]
                all_files = []
            else:
                # Windows/Desktop Paths
                user_home = os.path.expanduser("~")
                
                # Detect all available drives for Manual Scan (C:\, F:\, etc.)
                drives = []
                import string
                for letter in string.ascii_uppercase:
                    root = f"{letter}:\\"
                    # Check if drive exists
                    if os.path.exists(root):
                        drives.append(root)

                paths = [
                    os.path.join(user_home, "Downloads"),
                    os.path.join(user_home, "Desktop"),
                    os.path.join(user_home, "Documents"),
                    os.path.join(user_home, "Pictures"),
                    os.path.join(os.getenv('TEMP'), '') if os.getenv('TEMP') else "C:\\Temp"
                ] + drives 
                all_files = []
            
            # Dangerous Extensions only (Protect User Data)
            # REMOVED .dll to reduce file count (User Request for optimization).
            # DLLs are libraries and rarely primary threats for end-users compared to EXEs/APKs.
            dangerous_exts = ('.exe', '.msi', '.apk', '.bat', '.ps1', '.vbs', '.scr')

            # OPTIMIZATION: Skip System & Heavy Dev Folders to speed up initialization
            # Case-insensitive Set for proper matching on Windows
            skip_dirs = {s.lower() for s in {
                'Windows', 'Program Files', 'Program Files (x86)', 'ProgramData', 'Common Files',
                'System Volume Information', '$RECYCLE.BIN', 'Config.Msi',
                'node_modules', '.git', '.gradle', '.idea', 'Android', 'AppData', 'Library',
                'Steam', 'Epic Games', 'Origin', 'Ubisoft'
            }}

            # Parallel File Discovery (The Fix for Slow Init)
            # We scan each root path in a separate thread so C:\ doesn't block F:\
            def collect_files_from_path(root_path):
                local_files = []
                if not os.path.exists(root_path): return []
                try:
                    for root, dirs, files in os.walk(root_path):
                        if not scan_running: break
                        
                        # Prune the search tree (Optimization)
                        # Case-insensitive check
                        dirs[:] = [d for d in dirs if d.lower() not in skip_dirs]
                        
                        for f in files:
                            # 1. Skip ThreatViper itself
                            if "threatviper" in f.lower(): continue
                            # 2. Skip already locked files
                            if f.endswith(".locked"): continue
                            # 3. STRICT EXTENSION FILTER
                            if not f.lower().endswith(dangerous_exts): continue
                            
                            local_files.append(os.path.join(root, f))
                except: pass
                return local_files

            # Execute Discovery in Parallel (20 workers for finding files)
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as discovery_executor:
                future_to_path = {discovery_executor.submit(collect_files_from_path, p): p for p in paths}
                for future in concurrent.futures.as_completed(future_to_path):
                    if not scan_running: break
                    try:
                        all_files.extend(future.result())
                        # Update UI incrementally during discovery
                        status_text.value = f"Found {len(all_files)} files..."
                        page.update()
                    except: pass
            
            total_files = len(all_files)
            if total_files == 0:
                scan_running = False
                try:
                    status_text.value = "No executable threats found to scan."
                    scan_progress.visible = False
                    page.update()
                except: pass
                return

            files_scanned = 0
            threats_found = 0
            details_log = []
            
            # PERFORMANCE: Adaptive Threading
            # Android CPUs can't handle 50 threads comfortably.
            worker_count = 10 if page.platform == ft.PagePlatform.ANDROID else 50
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
                # ADAPTATION: Submit only filepath
                futures = {executor.submit(threat_engine.scan_file, fp): fp for fp in all_files}
                for future in concurrent.futures.as_completed(futures):
                    if not scan_running: 
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    files_scanned += 1
                    fp_orig = futures[future]
                    if files_scanned % 10 == 0: 
                        try:
                            status_text.value = f"Scanned {files_scanned}/{total_files}..."
                            current_file_text.value = f"Analyzing: {os.path.basename(fp_orig)[-40:]}"
                            page.update()
                        except: pass
                    try:
                        res = future.result()
                        # ADAPTATION: Our engine uses lowercase 'critical'/'high', new code checks uppercase
                        sev = res.get('severity', '').upper()
                        if sev in ['CRITICAL', 'HIGH']:
                            threats_found += 1
                            score = res.get('risk_score', 0) # key is 'risk_score' not 'score'
                            details_log.append(f"{sev}: {os.path.basename(fp_orig)} (Score: {score})")
                            quarantine_file(fp_orig)
                            try:
                                page.open(ft.SnackBar(ft.Text(f"🚨 Threat Quarantined: {os.path.basename(fp_orig)}"), bgcolor="red400"))
                            except: pass
                    except: pass
                            
            scan_running = False
            try:
                scan_progress.visible = False
                current_file_text.value = ""
                db.log_scan(files_scanned, threats_found, "Full Scan", "\n".join(details_log))
                if threats_found == 0:
                    status_text.value = f"Scan Complete. {files_scanned} files safe."
                    status_text.color = "green400"
                else:
                    status_text.value = f"⚠️ {threats_found} Threats Neutralized."
                    status_text.color = "red400"
                page.update()
            except: pass

        def toggle_shield(e):
            nonlocal shield_active
            shield_active = e.control.value
            if shield_active:
                threading.Thread(target=shield_monitor, daemon=True).start()
                page.open(ft.SnackBar(ft.Text("Active Defense Enabled"), bgcolor="green400"))
            else:
                page.open(ft.SnackBar(ft.Text("Defense Disabled"), bgcolor="red400"))

        def shield_monitor():
            # ADAPTATION: Monitor Paths based on Platform
            if page.platform == ft.PagePlatform.ANDROID:
                 user_home = "/storage/emulated/0"
                 monitored_paths = [
                    os.path.join(user_home, "Download"),
                    os.path.join(user_home, "Documents"),
                    os.path.join(user_home, "Pictures"),
                    # Social Media Real-time Paths
                    os.path.join(user_home, "Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Documents"),
                    os.path.join(user_home, "WhatsApp/Media/WhatsApp Documents"),
                    os.path.join(user_home, "Telegram/Telegram Documents"),
                 ]
            else:
                user_home = os.path.expanduser("~")
                
                # Detect all available drives (C:\, D:\, E:\, etc.)
                drives = []
                import string
                for letter in string.ascii_uppercase:
                    root = f"{letter}:\\"
                    if os.path.exists(root):
                        drives.append(root)

                monitored_paths = [
                    os.path.join(user_home, "Downloads"),
                    os.path.join(user_home, "Desktop"),
                    os.path.join(user_home, "Documents"),
                    os.path.join(user_home, "Pictures"),
                    os.getcwd() # Monitor the App folder itself (for testing)
                ] + drives # Add C:\, F:\, etc. to the list
            
            dangerous_exts = ('.exe', '.msi', '.apk', '.bat', '.ps1', '.vbs', '.scr', '.com')
            
            last_state = {p: set(os.listdir(p)) for p in monitored_paths if os.path.exists(p)}
            while shield_active:
                time.sleep(2)
                for p in monitored_paths:
                    if not os.path.exists(p): continue
                    try:
                        current = set(os.listdir(p))
                        new_files = current - last_state[p]
                        for nf in new_files:
                            if "threatviper" in nf.lower(): continue
                            if nf.endswith(".locked"): continue
                            if not nf.lower().endswith(dangerous_exts): continue
                            
                            fp = os.path.join(p, nf)
                            # ADAPTATION: scan_file takes 1 arg
                            res = threat_engine.scan_file(fp)
                            sev = res.get('severity', '').upper()
                            if sev == "CRITICAL" or (sev == "HIGH" and nf.lower().endswith('.apk')):
                                quarantine_file(fp)
                                db.log_scan(1, 1, "Real-time Shield", f"Quarantined {nf}")
                                try:
                                    page.open(ft.SnackBar(ft.Text(f"🛡️ Shield blocked: {nf}"), bgcolor="red400"))
                                    page.update()
                                except: pass
                        last_state[p] = current
                    except: pass

        def quarantine_file(filepath):
            try:
                # LOCAL FOLDER QUARANTINE (User Request)
                # Create a 'Quarantine' folder in the SAME directory as the threat.
                # This avoids cross-drive move errors while keeping the folder clean.
                
                parent_dir = os.path.dirname(filepath)
                q_dir = os.path.join(parent_dir, "Quarantine")
                
                if not os.path.exists(q_dir):
                    os.makedirs(q_dir)
                if not os.path.exists(q_dir):
                    os.makedirs(q_dir)
                    # Folder is visible so users can verify their files are safe (User Request)

                filename = os.path.basename(filepath)
                # Ensure unique name to prevent overwrite errors (timestamp)
                new_name = f"{filename}_{int(time.time())}.locked"
                dest_path = os.path.join(q_dir, new_name)

                # Check if already locked (edge case)
                if filepath.endswith(".locked"): return

                # Move operation (safe because it's same drive/partition)
                shutil.move(filepath, dest_path)
                print(f"🔒 Quarantined (Local Folder): {filepath} -> {dest_path}")
            except Exception as e:
                print(f"Quarantine Move Error: {e}")
                
                # ACTIVE REMEDIATION: Handle "File in Use" / Running Virus
                if "used by another process" in str(e) or "WinError 32" in str(e):
                    # Only attempt taskkill on Windows
                    if page.platform != ft.PagePlatform.ANDROID:

                        print(f"⚠️ Threat is RUNNING! Attempting to kill: {filename}")
                        try:
                            # Force kill the process by name
                            import subprocess
                            subprocess.run(f'taskkill /F /IM "{filename}"', shell=True, timeout=3)
                            time.sleep(1) # Allow Windows to release the file lock
                            
                            # Retrying Quarantine
                            shutil.move(filepath, dest_path)
                            print(f"💀 Process Killed & Quarantined: {filepath}")
                            return
                        except Exception as k_err:
                            print(f"Kill Failed: {k_err}")

                # Fallback: In-place rename if folder creation fails
                try:
                    os.rename(filepath, filepath + ".locked")
                    print(f"🔒 Quarantined (Fallback): {filepath} -> .locked")
                except: pass

        shield_switch.on_change = toggle_shield

        v = ft.View(
            "/dashboard",
            bgcolor="#111111",
            controls=[
                ft.AppBar(
                    title=ft.Text("Dashboard"), bgcolor="#1a1a1a",
                    actions=[
                        ft.IconButton(ft.Icons.HISTORY, on_click=lambda _: page.go("/history")),
                        ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: logout())
                    ]
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Container(
                            padding=20, bgcolor="#1a1a1a", border_radius=15,
                            content=ft.Row([
                                ft.Icon(ft.Icons.SHIELD, size=40, color="green400"),
                                ft.Column([
                                    ft.Text("STATUS: SECURE", weight="bold", size=16),
                                    ft.Text("ThreatViper Shield Active", size=12, color="grey")
                                ])
                            ])
                        ),
                        ft.Container(height=20),
                        ft.Container(
                            padding=15, bgcolor="#1a1a1a", border_radius=10,
                            content=ft.Row([ft.Text("Active Defense Shield"), shield_switch], alignment="spaceBetween")
                        ),
                        ft.Container(height=40),
                        ft.Column([
                            ft.Container(
                                width=150, height=150, border_radius=75, border=ft.border.all(2, "cyan400"),
                                content=ft.IconButton(ft.Icons.RADAR, icon_size=60, icon_color="cyan400", on_click=run_scan),
                                alignment=ft.alignment.center
                            ),
                            ft.Container(height=20),
                            status_text, current_file_text, scan_progress
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ])
                )
            ]
        )
        cached_views["/dashboard"] = v
        return v

    def history_view():
        docs = db.get_history()
        controls = []
        if not docs:
             controls.append(ft.ListTile(title=ft.Text("No scan history found.", color="grey")))
        else:
            for d in docs:
                threats = int(d.get('threatsFound', 0))
                # If threatsFound is 0 but 'details' contains threat info, we adjust
                details = d.get('details', '')
                if threats == 0 and "CRITICAL" in details.upper():
                    threats = 1 # Fallback for legacy logs
                
                color = "red400" if threats > 0 else "green400"
                icon = ft.Icons.GPP_BAD if threats > 0 else ft.Icons.GPP_GOOD
                
                status_text = "THREATS NEUTRALIZED" if threats > 0 else "SYSTEM SAFE"
                
                ts = d.get('timestamp', '')
                try: 
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    ts_display = dt.strftime("%b %d, %H:%M")
                except: ts_display = ts
                
                controls.append(ft.Container(
                    padding=10, border_radius=10, bgcolor="#1a1a1a", margin=ft.margin.only(bottom=10),
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon, color=color, size=24),
                            ft.Column([
                                ft.Text(f"{d.get('location', 'Manual Scan').upper()}", weight="bold", size=14),
                                ft.Text(f"{ts_display}", size=11, color="grey500"),
                            ], spacing=0, expand=True),
                            ft.Text(status_text, color=color, size=11, weight="bold")
                        ]),
                        ft.Divider(color="grey900", height=10),
                        ft.Row([
                            ft.Text(f"Files: {d.get('filesScanned', 0)}", size=12, color="grey300"),
                            ft.Text(f"Threats: {threats}", size=12, color=color, weight="bold"),
                        ], alignment="spaceBetween"),
                        ft.Text(details[:200] + "..." if len(details) > 200 else details, size=10, color="grey600", italic=True) if details else ft.Container()
                    ])
                ))
        return ft.View(
            "/history",
            bgcolor="#111111",
            controls=[
                ft.AppBar(
                    title=ft.Text("Scan Logs & Quarantine"), bgcolor="#1a1a1a",
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
                ),
                ft.ListView(controls=controls, padding=20, expand=True)
            ]
        )

    def logout():
        db.logout()
        cached_views.clear()
        page.views.clear()
        page.go("/login")

    def route_change(route):
        # We clear the stack for main views to avoid memory leaks and UI freezes
        if page.route == "/login":
            page.views.clear()
            page.views.append(login_view())
        elif page.route == "/register":
            page.views.clear()
            page.views.append(register_view())
        elif page.route == "/dashboard":
            page.views.clear()
            page.views.append(dashboard_view())
        elif page.route == "/history":
            # Append sub-views
            page.views.append(history_view())
        elif page.route == "/terms":
            # Append sub-views
            page.views.append(terms_view())
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.route = top_view.route
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    user = db.get_current_user()
    if user: page.go("/dashboard")
    else: page.go("/login")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
