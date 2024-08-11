import subprocess
import os
import sys

def create_and_run_batch_file(env_name, script_path, conda_executable):
    # Define the path for the batch file
    batch_file_path = "run_script.bat"
    
    # Create the content for the batch file
    batch_file_content = f"""
@echo off
{conda_executable} run -n {env_name} python {script_path}
pause
"""
    
    # Write the content to the batch file
    with open(batch_file_path, "w") as batch_file:
        batch_file.write(batch_file_content)
    
    # Command to open a new Command Prompt window and run the batch file
    start_command = f'start cmd /k "{batch_file_path}"'
    
    try:
        print(f"Opening new Command Prompt window to run script '{script_path}' in Conda environment '{env_name}'...")
        # Run the start command to open a new Command Prompt window
        subprocess.run(start_command, shell=True)
        print("Command Prompt window opened successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while opening Command Prompt window: {e}")
        sys.exit(1)

def main():
    env_name = "cellpose_env"  # Replace with your Conda environment name
    script_path = "path_to_your_python_script.py"  # Replace with the path to your Python script
    conda_executable = "conda"  # Replace with the path to your Conda executable if needed

    create_and_run_batch_file(env_name, script_path, conda_executable)

if __name__ == "__main__":
    main()
