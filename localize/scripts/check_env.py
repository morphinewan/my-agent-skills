import sys

def check_environment():
    print("Checking Python environment for Localization Skill...")
    
    # Check Python version (Require 3.6+)
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        return False
    
    print("Environment check passed.")
    
    # Check for jq
    import shutil
    if shutil.which("jq") is None:
        print("Error: 'jq' is required but not found. Please install it (e.g., brew install jq).")
        return False

    return True

if __name__ == "__main__":
    if check_environment():
        sys.exit(0)
    else:
        sys.exit(1)
