#!/usr/bin/env python3
"""
Final Build Script for ThreatViper Security
Creates a production-ready standalone .exe with bundled assets.
"""

import os
import sys
import subprocess
import shutil

def setup_environment():
    """Ensure all dependencies are ready for build"""
    print("🚀 Preparing build environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "flet", "appwrite", "scikit-learn", "numpy", "python-dotenv"])
    except:
        print("⚠️ Warning: Could not verify all dependencies, proceeding anyway...")

def build_executable():
    """Build the standalone EXE using PyInstaller"""
    print("🏗️ Building ThreatViper_Security.exe...")
    
    # Clean previous artifacts
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Define assets path
    # In Windows, we use ; for data separation in PyInstaller
    assets_flag = "assets;assets"
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'ThreatViper_Security',
        '--add-data', assets_flag,
        '--hidden-import', 'appwrite.services.account',
        '--hidden-import', 'appwrite.services.databases',
        '--hidden-import', 'sklearn.ensemble._isolation_forest',
        '--hidden-import', 'sklearn.ensemble._gb',
        '--hidden-import', 'sklearn.utils._cython_blas',
        '--hidden-import', 'sklearn.neighbors.typedefs',
        '--hidden-import', 'sklearn.neighbors.quad_tree',
        '--hidden-import', 'sklearn.tree._utils',
        '--clean',
        '--noconfirm',
        'main.py'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("✅ SUCCESS: ThreatViper_Security.exe created in 'dist/' folder.")
        print("="*50)
        
        # Add .env template for the user
        create_env_template()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Build failed with code {e.returncode}")

def create_env_template():
    """Create a template .env in the dist folder for the user"""
    env_content = """# ThreatViper Security - Configuration
# Please fill in your Appwrite details below
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_DB_ID=your_db_id
APPWRITE_COLLECTION_HISTORY=table_1
"""
    try:
        with open('dist/.env.template', 'w') as f:
            f.write(env_content)
        print("📝 Created .env.template in dist/ folder.")
    except: pass

if __name__ == "__main__":
    setup_environment()
    build_executable()