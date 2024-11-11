import json
import os

# Shared configuration dictionary
config = {}

def reload_config():
    """Reload the configuration from config.json located in the main directory."""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')  # Adjusts to main directory
    try:
        with open(file_path, 'r') as config_file:
            config.clear()  # Clear the current config
            config.update(json.load(config_file))  # Update config in-place
            print("Configuration reloaded successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: The configuration file contains invalid JSON.")
