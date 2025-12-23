#!/usr/bin/env python3
"""
First Run Setup for Jarvis Assistant
This ensures all directories and files are created before running main app
"""

import os
import sys
from pathlib import Path

def first_time_setup():
    """Create all necessary files and directories"""
    print("🚀 Setting up Jarvis Assistant for first run...")
    
    # Create directories
    directories = ['logs', 'images', 'examples']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created '{directory}/' directory")
    
    # Create log file
    log_file = Path('logs/jarvis.log')
    if not log_file.exists():
        log_file.touch(mode=0o666)
        print("✅ Created 'logs/jarvis.log' file")
    
    # Create README if doesn't exist
    if not os.path.exists('README.txt'):
        with open('README.txt', 'w') as f:
            f.write("Jarvis Assistant - First Run Complete!\n")
            f.write("Now run: python jarvis.py\n")
    
    print("\n🎉 Setup complete! You can now run:")
    print("   python jarvis.py")
    print("\nOr for help:")
    print("   python jarvis.py --help")
    
    return True

if __name__ == '__main__':
    first_time_setup()
    
    # Ask if user wants to run jarvis now
    response = input("\nRun Jarvis now? (y/N): ").strip().lower()
    if response == 'y':
        print("\nStarting Jarvis...")
        os.system('python jarvis.py')
