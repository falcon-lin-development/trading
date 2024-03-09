# setup.py in a subfolder
import os
import sys
import subprocess

def find_git_root(start_path):
    try:
        # Run the git rev-parse command to find the git root directory
        git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=start_path, text=True).strip()
        return git_root
    except subprocess.CalledProcessError:
        # Git command failed, which likely means we're not in a git repo
        raise FileNotFoundError("Git repository root not found. Are you in a Git repository?")

def find_project_root_with_git_scope(current_path, marker):
    git_root = find_git_root(current_path)
    project_root = current_path
    
    while not os.path.exists(os.path.join(project_root, marker)):
        if project_root == git_root:
            # We've reached the git root without finding the marker
            raise FileNotFoundError(f"Marker '{marker}' not found within the Git repository.")
        
        new_root = os.path.dirname(project_root)
        if new_root == project_root:
            # The root of the filesystem has been reached without finding the marker
            raise FileNotFoundError(f"Unable to find the project root. Marker: {marker}")
        project_root = new_root
    
    return project_root

def init():
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = find_project_root_with_git_scope(current_path, marker='settings.py')

    # Add the project root to sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added project root to sys.path: {project_root}")

    # Now it's safe to import settings
    from settings import BASE_DIR, DATA_DIR, CONTANT_DIR

    os.chdir(BASE_DIR) # Change the current working directory to the project root
    print(f"Changed current working directory to: {BASE_DIR}")
    print(f"Initialized project with base directory: {BASE_DIR}")


    # Create DATA_DIR and CONTANT_DIR if they do not exist
    for directory in [DATA_DIR, CONTANT_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory at {directory}")
