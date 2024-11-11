import os
import platform

def get_venv_python(venv_name):
    # Get the current directory (main folder where the venv is located)
    base_dir = os.getcwd()
    
    # Build the path to the venv
    venv_path = os.path.join(base_dir, venv_name)
    
    # Determine the path to the python executable inside the venv
    if platform.system() == 'Windows':
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(venv_path, 'bin', 'python')

    if os.path.exists(python_path):
        return python_path
    else:
        raise FileNotFoundError(f"Could not find Python executable for venv: {venv_name}")
