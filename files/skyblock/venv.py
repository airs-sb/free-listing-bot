import os
import platform

# Function to activate venv based on the name
def get_venv_python(venv_name):
    # Automatically find the main folder based on script location
    base_dir = os.path.dirname(os.path.realpath(__file__))  # Get the current directory (main folder)
    
    # Build the path to the venv
    venv_path = os.path.join(base_dir, "..", "..", '..', venv_name)  # Adjusted to go two directories up

    if platform.system() == 'Windows':
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(venv_path, 'bin', 'python')

    if os.path.exists(python_path):
        return python_path
    else:
        raise FileNotFoundError(f"Could not find Python executable for venv: {venv_name}")
