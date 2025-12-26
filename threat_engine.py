import os
import math
import hashlib
import re

# Dependency Imports (Graceful failover)
try:
    import yara
    HAS_YARA = True
except ImportError:
    HAS_YARA = False

try:
    import pefile
    HAS_PEFILE = True
except ImportError:
    HAS_PEFILE = False

class ThreatEngine:
    def __init__(self, rules_path='yara_rules.yar'):
        self.rules = None
        # Expanded Whitelist
        self.whitelist = [
            'chrome.exe', 'explorer.exe', 'svchost.exe', 'firefox.exe',
            'wix', 'msbuild', 'python', 'pip', 'node', 'git', 'visual studio',
            'nvidia', 'amd', 'intel', 'setup', 'installer'
        ]
        
        # Initialize YARA
        if HAS_YARA:
            if os.path.exists(rules_path):
                try:
                    self.rules = yara.compile(filepath=rules_path)
                    print(f"✅ YARA Rules Loaded: {rules_path}")
                except Exception as e:
                    print(f"⚠️ YARA Error: {e}")
            else:
                print(f"⚠️ YARA Rules not found at {rules_path}")
        else:
            print("⚠️ YARA module not installed. Content scanning limited.")

    def scan_file(self, filepath):
        """
        Deep Scan a single file using Hybrid Analysis (Metadata + Content + Rules).
        Returns dict with severity, score, and details.
        """
        result = {
            "filename": os.path.basename(filepath),
            "score": 0,
            "severity": "SAFE",
            "details": []
        }

        if not os.path.exists(filepath):
            return result

        try:
            # 1. METADATA ANALYSIS (Fast)
            # ---------------------------
            filename = os.path.basename(filepath).lower()
            
            # Whitelist Check (Fast Pass)
            if any(safe in filename for safe in self.whitelist):
                # APK exception: APKs are never fully whitelisted if they are truly malicious, 
                # but for simplicity in this engine, we allow whitelisted tools to pass.
                # If you want Strict APK quarantine, uncomment the next line:
                # if not filename.endswith('.apk'): return result
                return result
            
            # Extension Risk
            if filename.endswith('.apk'):
                result['score'] += 100
                result['details'].append("Critical: Unauthorized APK Package")
            elif filename.endswith(('.scr', '.bat', '.ps1', '.vbs')):
                result['score'] += 20
            elif filename.endswith('.exe'):
                result['score'] += 10 # Reduced from 20 for standard EXEs
            
            # Entropy (Randomness) Check
            entropy = self._get_entropy(filepath)
            if entropy > 7.2:
                # Installers often have high entropy, so we only add points if it's not a common installer name
                if not any(x in filename for x in ['setup', 'install', 'update']):
                    result['score'] += 20 # Reduced from 30
                    result['details'].append(f"High Entropy ({entropy:.2f})")

            # 2. CONTENT ANALYSIS (Deep)
            # --------------------------
            
            # YARA Scanning (Pattern Matching)
            if self.rules:
                try:
                    matches = self.rules.match(filepath)
                    for match in matches:
                        risk = match.meta.get('severity', 'Medium')
                        points = 50 if risk == 'Critical' else (30 if risk == 'High' else 10)
                        result['score'] += points
                        result['details'].append(f"YARA Match: {match.rule} [{risk}]")
                except Exception as e:
                    print(f"YARA Scan Error: {e}")

            # PE Structure Analysis (Windows Executables)
            if HAS_PEFILE and filename.endswith(('.exe', '.dll', '.sys')):
                pe_issues = self._analyze_pe(filepath)
                if pe_issues:
                    # Cap PE score to prevent legitimate packed apps from triggers
                    pe_score = min(30, len(pe_issues) * 10) 
                    result['score'] += pe_score
                    result['details'].extend(pe_issues)

            # 3. VERDICT
            # ----------
            # Increased SAFE threshold slightly to be more tolerant
            if result['score'] >= 85:
                result['severity'] = "CRITICAL"
            elif result['score'] >= 60:
                result['severity'] = "HIGH"
            elif result['score'] >= 30:
                result['severity'] = "MEDIUM"
            else:
                result['severity'] = "SAFE"

        except Exception as e:
            result['details'].append(f"Scan Error: {str(e)}")
        
        # Add risk_score for main.py compatibility
        result['risk_score'] = result['score']
        return result

    def _get_entropy(self, filepath):
        """Calculates Shannon Entropy of the file content"""
        # Read first 1MB only for speed
        try:
            with open(filepath, 'rb') as f:
                data = f.read(1024 * 1024)
            if not data: return 0.0
            
            entropy = 0
            for x in range(256):
                p_x = float(data.count(x)) / len(data)
                if p_x > 0:
                    entropy += - p_x * math.log(p_x, 2)
            return entropy
        except: return 0.0

    def _analyze_pe(self, filepath):
        """Checks for suspicious PE characteristics"""
        issues = []
        try:
            pe = pefile.PE(filepath)
            # Check sections for high entropy (packing)
            for section in pe.sections:
                if section.get_entropy() > 7.4:
                    issues.append(f"Packed Section: {section.Name.decode('utf-8', 'ignore').strip()}")
            
            # Check suspicious imports
            bad_imports = ['WriteProcessMemory', 'CreateRemoteThread', 'VirtualAllocEx']
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name and imp.name.decode('utf-8', 'ignore') in bad_imports:
                            issues.append(f"Suspicious API: {imp.name.decode('utf-8', 'ignore')}")
        except: pass
        return issues
