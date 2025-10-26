#!/usr/bin/env python
"""
Setup script to fix dependencies and prepare the scanner application
"""
import subprocess
import sys

def run_command(cmd):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")
    return result.returncode

def main():
    """Setup the application"""
    print("=" * 60)
    print("🔧 Setting up Fyers Intraday Scanner")
    print("=" * 60)

    # Uninstall problematic jose package
    print("\n1. Removing incompatible jose package...")
    run_command(f"{sys.executable} -m pip uninstall -y jose")

    # Install requirements
    print("\n2. Installing dependencies...")
    return_code = run_command(f"{sys.executable} -m pip install -r requirements.txt")

    if return_code == 0:
        print("\n" + "=" * 60)
        print("✅ Setup complete!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  python run.py")
        print("\nOr:")
        print("  python main.py")
        print()
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
