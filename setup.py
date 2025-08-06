#!/usr/bin/env python3
"""
Setup script for ai_app project
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    # Install minimal requirements first
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_minimal.txt"])
        print("✅ Minimal requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing minimal requirements: {e}")
        return False
    
    # Install playwright browsers
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])
        print("✅ Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing playwright browsers: {e}")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'requests',
        'pandas',
        'numpy',
        'pandas_ta',
        'groq',
        'jwt',
        'cryptography',
        'plotly',
        'playwright',
        'schedule'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'data',
        'data/charts',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up ai_app project...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during requirements installation")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Setup failed during dependency check")
        return False
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your API keys in config.py")
    print("2. Test the installation: python main.py")
    print("3. Check the documentation in IBKR_README.md")
    
    return True

if __name__ == "__main__":
    main() 