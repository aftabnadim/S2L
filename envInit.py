import os
import subprocess
import urllib.request
import platform

def get_conda_path():
    user_name = os.getlogin()
    return f"C:\\Users\\{user_name}\\Miniconda3\\Scripts\\conda.exe"

def is_conda_installed():
    conda_executable = get_conda_path()
    try:
        subprocess.run([conda_executable, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_conda_with_winget():
    print("Installing Miniconda using winget...")
    try:
        subprocess.run(["winget", "install", "-e", "--id", "Anaconda.Miniconda3"], check=True)
        os.environ["PATH"] = f"C:\\Users\\{os.getlogin()}\\Miniconda3\\Scripts" + os.pathsep + os.environ["PATH"]
    except subprocess.CalledProcessError:
        print("Failed to install Miniconda using winget.")
        raise

def download_and_install_conda():
    system = platform.system().lower()
    if system == "windows":
        install_conda_with_winget()
    else:
        conda_installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        installer_path = "/tmp/miniconda_installer.sh"
        install_command = ["bash", installer_path, "-b", "-p", os.path.expanduser("~/miniconda")]
        conda_bin_path = os.path.expanduser("~/miniconda/bin")
        
        print("Downloading Miniconda installer...")
        urllib.request.urlretrieve(conda_installer_url, installer_path)
        
        print("Installing Miniconda...")
        subprocess.run(install_command, check=True)
        
        os.environ["PATH"] = conda_bin_path + os.pathsep + os.environ["PATH"]

def environment_exists(env_name):
    conda_executable = get_conda_path()
    try:
        result = subprocess.run([conda_executable, "env", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return env_name in result.stdout
    except subprocess.CalledProcessError:
        return False

def create_conda_env(env_name, python_version, requirements_file=None):
    conda_executable = get_conda_path()
    print(f"Creating Conda environment '{env_name}' with Python {python_version}...")
    subprocess.run([conda_executable, "create", "-y", "-n", env_name, f"python={python_version}"], check=True)
    
    if requirements_file and os.path.isfile(requirements_file):
        print(f"Installing packages from {requirements_file} in the Conda environment '{env_name}'...")
        subprocess.run([conda_executable, "run", "-n", env_name, "pip", "install", "-r", requirements_file], check=True)

def install_cellpose(env_name):
    conda_executable = get_conda_path()
    print(f"Installing Cellpose in the Conda environment '{env_name}'...")
    subprocess.run([conda_executable, "run", "-n", env_name, "pip", "install", "cellpose"], check=True)

def remove_torch(env_name):
    conda_executable = get_conda_path()
    print(f"Removing Torch from the Conda environment '{env_name}'...")
    subprocess.run([conda_executable, "run", "-n", env_name, "pip", "uninstall", "-y", "torch"], check=True)

def install_latest_torch(env_name, use_cuda):
    conda_executable = get_conda_path()
    if use_cuda:
        print(f"Installing the CUDA version of Torch, Torchvision, and Torchaudio in the Conda environment '{env_name}'...")
        subprocess.run([conda_executable, "run", "-n", env_name, "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu124"], check=True)
    else:
        print(f"Installing the CPU version of Torch, Torchvision, and Torchaudio in the Conda environment '{env_name}'...")
        subprocess.run([conda_executable, "run", "-n", env_name, "pip", "install", "torch", "torchvision", "torchaudio"], check=True)

# Main execution
if not is_conda_installed():
    download_and_install_conda()

env_name = "cellpose_env"
python_version = "3.8"
requirements_file = "AutomationFolder/requirements.txt"  # Path to your requirements file

# Check if environment exists
if not environment_exists(env_name):
    create_conda_env(env_name, python_version, requirements_file)
    # Prompt user to choose CUDA or CPU version of Torch when creating the environment
    use_cuda = input("Do you want to install the CUDA version of Torch? (yes/no): ").strip().lower() == "yes"
    install_latest_torch(env_name, use_cuda)
    install_cellpose(env_name)
else:
    # Do nothing if the environment already exists
    print(f"The Conda environment '{env_name}' already exists. No further action is taken.")
