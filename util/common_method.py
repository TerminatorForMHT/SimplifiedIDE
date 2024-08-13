import os
import subprocess
from pathlib import Path
from sys import platform


def find_python_paths():
    # Use the PATH environment variable
    path_env = os.getenv('PATH', '').split(os.pathsep)

    # Common directories to check
    common_paths = [
        "/usr/bin",
        "/usr/local/bin",
        "/opt/local/bin",
        "/opt/bin",
        "/bin",
        "/sbin",
        str(Path.home() / "anaconda3" / "bin"),
        str(Path.home() / ".local" / "bin"),
        "C:\\Python27",
        "C:\\Python37",
        "C:\\Python39",
        "C:\\Users\\{username}\\AppData\\Local\\Programs\\Python\\Python{version}",
        "C:\\Program Files (x86)\\Python{version}",
        "C:\\Program Files\\Python{version}"
    ]

    # Collect all directories to check
    search_paths = set(path_env + common_paths)

    # Extensions to check for
    executable_names = ["python", "python3", "python2"]
    executable_extensions = ["", ".exe", ".bat"]

    # Found Python paths
    python_paths = set()

    for directory in search_paths:
        for executable in executable_names:
            for ext in executable_extensions:
                potential_path = Path(directory) / (executable + ext)
                if potential_path.exists() and os.access(potential_path, os.X_OK):
                    python_paths.add(str(potential_path.resolve()))

    return sorted(python_paths)


def create_and_activate_virtual_environment(target_path, env_name, base_python_path):
    env_path = os.path.join(target_path, env_name)
    try:
        # Create virtual environment
        subprocess.run([base_python_path, '-m', 'venv', env_path], check=True)
        print(f"Virtual environment '{env_name}' created successfully at {env_path}")

        # Determine the activation command based on the operating system
        if platform == "Windows":
            activate_command = os.path.join(env_path, 'Scripts', 'activate')
            activation_cmd = f'cmd /k "{activate_command}"'
        else:
            activate_command = os.path.join(env_path, 'bin', 'activate')
            activation_cmd = f'bash --rcfile <(echo ". {activate_command}")'

        # Activate the virtual environment
        subprocess.run(activation_cmd, shell=True)
        return (0, f"Virtual environment '{env_name}' activated.")
    except subprocess.CalledProcessError as e:
        return (1, f"Error occurred while creating or activating virtual environment: {e}")
