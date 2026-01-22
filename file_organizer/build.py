"""
Build script for creating a standalone executable with PyInstaller.
"""
import subprocess
import sys
import shutil
import os
from pathlib import Path

def build():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=FileOrganizer",
        "--onefile",
        # Note: --windowed flag removed - this is a CLI tool and needs console output
        "--add-data", f"config{os.pathsep}config",
        "--add-data", f"webui/templates{os.pathsep}webui/templates",
        "--hidden-import=win32file",
        "--hidden-import=win32api",
        "--hidden-import=sqlite3",
        "--hidden-import=yaml",
        "--hidden-import=tqdm",
        "--hidden-import=PIL",
        "--hidden-import=python_docx",
        "--hidden-import=PyPDF2",
        "--hidden-import=exifread",
        "--hidden-import=flask",
        "--clean",
        "src/main.py"
    ]

    print("Running PyInstaller...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: PyInstaller build failed: {e}")
        sys.exit(1)

    # Note: With --onefile, resources are embedded in the executable.
    # No need to copy additional files - they're accessed via PyInstaller's runtime hooks.

    exe_name = "FileOrganizer.exe" if os.name == 'nt' else "FileOrganizer"
    print(f"Build completed successfully. Executable is in dist/{exe_name}")

if __name__ == "__main__":
    build()