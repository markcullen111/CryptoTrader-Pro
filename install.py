#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path
import subprocess
import platform

def print_colored(text, color):
    """Print colored text."""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    if platform.system() != 'Windows':
        print(f"{colors[color]}{text}{colors['end']}")
    else:
        print(text)

def check_python_version():
    """Check if Python version is compatible."""
    print_colored("Checking Python version...", "blue")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored("Error: Python 3.8 or higher is required", "red")
        sys.exit(1)
    print_colored("✓ Python version check passed", "green")

def setup_virtual_environment():
    """Create and activate virtual environment."""
    print_colored("\nSetting up virtual environment...", "blue")
    
    if os.path.exists("venv"):
        print_colored("Found existing virtual environment", "yellow")
        choice = input("Do you want to recreate it? (y/N): ").lower()
        if choice == 'y':
            shutil.rmtree("venv")
        else:
            return

    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✓ Virtual environment created", "green")
    except subprocess.CalledProcessError:
        print_colored("Error: Failed to create virtual environment", "red")
        sys.exit(1)

def install_dependencies():
    """Install required packages."""
    print_colored("\nInstalling dependencies...", "blue")
    
    # Activate virtual environment
    if platform.system() == 'Windows':
        python_path = os.path.join("venv", "Scripts", "python")
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        python_path = os.path.join("venv", "bin", "python")
        pip_path = os.path.join("venv", "bin", "pip")

    try:
        # Upgrade pip
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print_colored("✓ Dependencies installed", "green")
    except subprocess.CalledProcessError:
        print_colored("Error: Failed to install dependencies", "red")
        sys.exit(1)

def setup_configuration():
    """Set up configuration files."""
    print_colored("\nSetting up configuration...", "blue")
    
    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Copy config template if it doesn't exist
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        shutil.copy("config/config.yaml.template", config_file)
        print_colored("✓ Created config.yaml from template", "green")
    else:
        print_colored("Config file already exists", "yellow")
    
    # Copy .env template if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        shutil.copy(".env.template", env_file)
        print_colored("✓ Created .env from template", "green")
    else:
        print_colored("Environment file already exists", "yellow")

def setup_database():
    """Initialize the database."""
    print_colored("\nSetting up database...", "blue")
    
    try:
        if platform.system() == 'Windows':
            python_path = os.path.join("venv", "Scripts", "python")
        else:
            python_path = os.path.join("venv", "bin", "python")
            
        subprocess.run([python_path, "setup_database.py"], check=True)
        print_colored("✓ Database setup complete", "green")
    except subprocess.CalledProcessError:
        print_colored("Error: Failed to setup database", "red")
        sys.exit(1)

def create_required_directories():
    """Create required directories."""
    print_colored("\nCreating required directories...", "blue")
    directories = ["data", "logs", "models"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print_colored("✓ Created required directories", "green")

def main():
    """Main installation function."""
    print_colored("\n=== CryptoTrader Pro Installation ===\n", "blue")
    
    # Check Python version
    check_python_version()
    
    # Setup virtual environment
    setup_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create required directories
    create_required_directories()
    
    # Setup configuration
    setup_configuration()
    
    # Setup database
    setup_database()
    
    print_colored("\n=== Installation Complete! ===\n", "green")
    print_colored("To start the application:", "blue")
    if platform.system() == 'Windows':
        print("1. Run: run.bat")
    else:
        print("1. Run: ./run.sh")
    print("\n2. Open your web browser and go to: http://localhost:8501")
    print("\nMake sure to edit the following files with your settings:")
    print("- config/config.yaml")
    print("- .env")

if __name__ == "__main__":
    main() 