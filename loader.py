import argparse
import envInit
#import downloadNeccesaryLibs
import runGUI
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Setup and run script in a Conda environment.")
    parser.add_argument("--use-cuda", action="store_true", help="Specify to install CUDA version of PyTorch.")
   # parser.add_argument("--zip", required=True, help="URL to necessary files to exec.")
    parser.add_argument("--script", required=False,default='main.py' ,help="File name for executing. Defaults to main.py.")
    args = parser.parse_args()

    env_name = "cellpose_env"
    python_version = "3.8"
    
    # Initialize Conda environment
    condaPath = envInit.get_conda_path()
    if not envInit.is_conda_installed():
        try:
            envInit.download_and_install_conda()
        except Exception as e:
            print(f"Error during Conda installation: {e}")
            sys.exit(1)

    if not envInit.environment_exists(env_name):
        envInit.create_conda_env(env_name, python_version)
        envInit.install_cellpose(env_name)
        
        if args.use_cuda:
            envInit.remove_torch(env_name)
            envInit.install_latest_torch(env_name, use_cuda=True)
        else:
            envInit.install_latest_torch(env_name, use_cuda=False)
        
        envInit.install_additional_libraries(env_name)
    else:
        print(f"Conda environment '{env_name}' already exists. Skipping environment setup.")

    # Download necessary libraries
    #downloadNeccesaryLibs.main(args.zip)

    # Run the main script inside the Conda environment
    
    fullPath = f"AutomationFolder/{args.script}"
    
    
    runGUI.create_and_run_batch_file(env_name, fullPath, condaPath)

if __name__ == "__main__":
    main()
