#!/usr/bin/env python3
"""
College ERP System Setup Script
This script automates the initial setup process
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a system command with error handling"""
    print(f"\n🔄 {description}...")
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists('venv'):
        run_command('python -m venv venv', 'Creating virtual environment')
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install required Python packages"""
    if platform.system() == 'Windows':
        pip_command = 'venv\\Scripts\\pip install -r requirements.txt'
    else:
        pip_command = 'venv/bin/pip install -r requirements.txt'
    
    run_command(pip_command, 'Installing dependencies')

def setup_database():
    """Set up the database with initial migrations"""
    if platform.system() == 'Windows':
        python_command = 'venv\\Scripts\\python'
    else:
        python_command = 'venv/bin/python'
    
    run_command(f'{python_command} manage.py makemigrations', 'Creating migrations')
    run_command(f'{python_command} manage.py migrate', 'Applying migrations')

def create_sample_data():
    """Create sample data for testing"""
    if platform.system() == 'Windows':
        python_command = 'venv\\Scripts\\python'
    else:
        python_command = 'venv/bin/python'
    
    choice = input("\\n📝 Do you want to create sample data? (y/N): ").lower()
    if choice in ['y', 'yes']:
        run_command(f'{python_command} manage.py create_sample_data', 'Creating sample data')
        print("\\n👥 Demo users created:")
        print("   Admin: admin/admin123")
        print("   Teacher: teacher1/teacher123") 
        print("   Student: student1/student123")

def create_superuser():
    """Create Django superuser"""
    choice = input("\\n🔐 Do you want to create a superuser? (y/N): ").lower()
    if choice in ['y', 'yes']:
        if platform.system() == 'Windows':
            python_command = 'venv\\Scripts\\python'
        else:
            python_command = 'venv/bin/python'
        
        print("\\n📝 Please enter superuser details:")
        os.system(f'{python_command} manage.py createsuperuser')

def main():
    """Main setup function"""
    print("🎓 College ERP System Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Setup steps
    setup_virtual_environment()
    install_dependencies()
    setup_database()
    create_sample_data()
    create_superuser()
    
    print("\\n🎉 Setup completed successfully!")
    print("\\n🚀 To start the development server, run:")
    if platform.system() == 'Windows':
        print("   venv\\Scripts\\activate")
        print("   python manage.py runserver")
    else:
        print("   source venv/bin/activate")
        print("   python manage.py runserver")
    
    print("\\n🌐 Then open http://127.0.0.1:8000/ in your browser")
    print("\\n📚 Check README.md for more information")

if __name__ == "__main__":
    main()
