import os
import sys
import pkg_resources
import importlib

def check_setup():
    """Check if all requirements are met"""
    print("Checking ARGUS RAG system setup...")
    
    # Check Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    
    # Check if Final_ARGUS_Thirdparty.py exists
    thirdparty_path = os.path.join(current_dir, "Final_ARGUS_Thirdparty.py")
    if os.path.exists(thirdparty_path):
        print("✓ Final_ARGUS_Thirdparty.py found")
    else:
        print("✗ Final_ARGUS_Thirdparty.py not found!")
    
    # Check required packages
    required = {
        'streamlit': '1.31.1',
        'pandas': '2.1.4',
        'plotly': '5.18.0',
        'requests': '2.31.0',
        'python-dotenv': '1.0.0'
    }
    
    for package, version in required.items():
        try:
            importlib.import_module(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed!")

if __name__ == "__main__":
    check_setup()
